#!/usr/bin/env python3
"""Reusable Agnes image/video CLI. Task content belongs in config/arguments."""
import argparse
import base64
import copy
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

VERSION = '1.0.0'
DEFAULT_BASE = 'https://apihub.agnes-ai.com/v1'
TERMINAL = {'completed', 'failed', 'cancelled', 'canceled'}
RETRYABLE = {408, 429, 500, 502, 503, 504, 520, 522, 524}


class AgnesError(Exception):
    pass


class HTTPFailure(AgnesError):
    def __init__(self, status, retry_after=0):
        super().__init__(f'Agnes HTTP {status}; generation POST is never auto-retried.')
        self.status, self.retry_after = status, retry_after


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, obj, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, indent=2)
    if exclusive:
        with path.open('x', encoding='utf-8') as f:
            f.write(data)
    else:
        temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
        temp.write_text(data, encoding='utf-8')
        temp.replace(path)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(value):
    """Console/preflight output: no credentials, embedded image bytes, signed queries."""
    if isinstance(value, dict):
        return {k: ('[REDACTED]' if k.lower() in {'api_key','authorization','token','b64_json'} else safe(v)) for k,v in value.items()}
    if isinstance(value, list):
        return [safe(v) for v in value]
    if isinstance(value, str):
        if value.startswith('data:'):
            return f'[inline media, {len(value)} characters]'
        if value.startswith('https://'):
            u = urllib.parse.urlsplit(value)
            return urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,'',''))
    return value


def https_url(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.fragment:
        raise AgnesError('Expected an HTTPS URL without embedded credentials or fragment.')
    return url


def base_url(url):
    https_url(url)
    u = urllib.parse.urlsplit(url)
    if u.query or not u.path.rstrip('/').endswith('/v1'):
        raise AgnesError('base_url must end in /v1 and have no query.')
    return url.rstrip('/')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AgnesError('Authenticated API redirect refused; verify endpoint explicitly.')


def api(method, url, key, payload=None, timeout=120):
    # There is intentionally no POST retry and no automatic domain fallback.
    request = urllib.request.Request(https_url(url), method=method,
        data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode('utf-8'),
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        retry_after = exc.headers.get('Retry-After', '0')
        raise HTTPFailure(exc.code, float(retry_after) if retry_after.isdigit() else 0) from None
    except (OSError, ValueError) as exc:
        # Do not echo provider bodies, request bodies, proxy URLs or secrets.
        raise AgnesError(f'API transport/response failure: {type(exc).__name__}') from None
    if not isinstance(result, dict):
        raise AgnesError('API response is not a JSON object.')
    return result


def image_input(source, origin, transport):
    from PIL import Image, ImageOps
    if source.startswith('https://'):
        return https_url(source), {'source':source,'transport':'https'}
    if source.startswith('data:'):
        if not re.match(r'^data:image/(png|jpeg|webp);base64,',source):
            raise AgnesError('Only PNG/JPEG/WebP image Data URIs are supported.')
        try:
            data = base64.b64decode(source.split(',',1)[1],validate=True)
        except ValueError:
            raise AgnesError('Invalid image Base64.') from None
        label = '[provided Data URI]'
    else:
        path = Path(source)
        path = (origin/path).resolve() if not path.is_absolute() else path.resolve()
        data, label = path.read_bytes(), str(path)
    source_hash = digest(data)
    with Image.open(io.BytesIO(data)) as original:
        original.load()
        if original.format not in {'PNG','JPEG','WEBP'}:
            raise AgnesError('Reference image must be PNG, JPEG or WebP.')
        orientation_changed = original.getexif().get(274,1) != 1
        im = ImageOps.exif_transpose(original)
        fmt = transport.get('format','original').lower()
        max_edge = int(transport.get('max_edge',0))
        quality = int(transport.get('quality',94))
        if max_edge < 0 or not 1 <= quality <= 100 or fmt not in {'original','png','jpeg','webp'}:
            raise AgnesError('Invalid transport max_edge/quality/format.')
        resized = max_edge > 0 and max(im.size) > max_edge
        if resized:
            im.thumbnail((max_edge,max_edge),Image.Resampling.LANCZOS)
        output_fmt = original.format if fmt == 'original' else fmt.upper()
        # Preserve transparency when requested by original/PNG/WebP. JPEG is explicit.
        if fmt != 'original' or resized or orientation_changed:
            if output_fmt == 'JPEG':
                rgba = im.convert('RGBA')
                flat = Image.new('RGB', im.size, 'white')
                flat.paste(rgba, mask=rgba.getchannel('A'))
                im = flat
            buf = io.BytesIO()
            options = {'quality':quality} if output_fmt in {'JPEG','WEBP'} else {}
            if output_fmt == 'JPEG': options['subsampling'] = 0
            im.save(buf, format=output_fmt, **options)
            data = buf.getvalue()
        width,height = im.size
        mime = {'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp'}[output_fmt]
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode('ascii'), dict(
        source=label, source_sha256=source_hash, submitted_sha256=digest(data),
        bytes=len(data), width=width,height=height, mime=mime)


def load_config(args):
    origin = Path(args.config).resolve().parent if args.config else Path.cwd()
    cfg = read_json(args.config) if args.config else {}
    known = {'kind','model','prompt','prompt_file','output_dir','output_name','base_url',
             'api_key_env','parameters','images','first_frame','last_frame','audios','videos',
             'transport','timeout','poll_interval','max_wait','response_format'}
    if not isinstance(cfg,dict) or set(cfg)-known:
        raise AgnesError('Unknown configuration keys: '+str(set(cfg)-known if isinstance(cfg,dict) else 'not an object'))
    cfg = copy.deepcopy(cfg)
    for key in ('kind','model','output_name','base_url','api_key_env','timeout','poll_interval','max_wait','response_format'):
        value = getattr(args,key,None)
        if value is not None: cfg[key] = value
    for key in ('prompt_file','output_dir'):
        value = getattr(args,key,None)
        if value is not None: cfg[key] = str(Path(value).resolve())
    if getattr(args,'prompt',None) is not None:
        cfg.pop('prompt_file',None)
        cfg['prompt'] = args.prompt
    elif getattr(args,'prompt_file',None) is not None:
        cfg.pop('prompt',None)
    if getattr(args,'image',None) is not None:
        cfg['images'] = [v if v.startswith(('https://','data:')) else str(Path(v).resolve()) for v in args.image]
    for key in ('first_frame','last_frame'):
        value = getattr(args,key,None)
        if value is not None: cfg[key] = value if value.startswith(('https://','data:')) else str(Path(value).resolve())
    params = cfg.setdefault('parameters',{})
    if getattr(args,'parameters_json',None): params.update(read_json(args.parameters_json))
    for key in ('seconds','size','aspect_ratio','mode','seed'):
        value = getattr(args,key,None)
        if value is not None: params['ratio' if key == 'aspect_ratio' and cfg.get('kind') == 'image' else key] = value
    transport = cfg.setdefault('transport',{})
    for arg,key in [('max_edge','max_edge'),('image_format','format'),('jpeg_quality','quality')]:
        value = getattr(args,arg,None)
        if value is not None: transport[key] = value
    cfg['base_url'] = base_url(cfg.get('base_url', os.getenv('AGNES_BASE_URL') or DEFAULT_BASE))
    cfg.setdefault('api_key_env','AGNES_API_KEY')
    if cfg.get('kind') not in {'image','video'} or not cfg.get('model'):
        raise AgnesError('kind (image/video) and model are required; no implicit model substitution.')
    if bool(cfg.get('prompt')) == bool(cfg.get('prompt_file')):
        raise AgnesError('Provide exactly one prompt or prompt_file.')
    if cfg.get('prompt_file'):
        cfg['prompt'] = (origin/Path(cfg['prompt_file'])).read_text(encoding='utf-8-sig')
    if not cfg['prompt'].strip(): raise AgnesError('Prompt is empty.')
    if not cfg.get('output_dir'): raise AgnesError('output_dir is required.')
    cfg['output_dir'] = str((origin/Path(cfg['output_dir'])).resolve())
    name = cfg.get('output_name','result')
    if not name or name in {'.','..'} or re.search(r'[<>:"/\\|?*\x00-\x1f]',name):
        raise AgnesError('output_name must be a safe basename without extension or directory.')
    cfg['output_name'] = name
    for key,default in [('timeout',120),('poll_interval',30),('max_wait',600)]:
        cfg.setdefault(key,default)
        if not isinstance(cfg[key],(int,float)) or cfg[key] <= 0: raise AgnesError(key+' must be positive.')
    return cfg, origin


def build_payload(cfg, origin):
    params = copy.deepcopy(cfg.get('parameters',{}))
    reserved = {'model','prompt','images','image','first_frame','last_frame','audios','videos',
                'api_key','authorization','headers','base_url'}
    if reserved & params.keys(): raise AgnesError('Use dedicated configuration fields for '+str(reserved & params.keys()))
    if cfg['kind'] == 'image' and 'response_format' in params:
        raise AgnesError('Use response_format config/CLI, not parameters.response_format.')
    payload = dict(params, model=cfg['model'],prompt=cfg['prompt'])
    entries, images = [], []
    for source in cfg.get('images',[]):
        uri,entry = image_input(source,origin,cfg.get('transport',{}))
        entry['slot'] = f'Picture {len(images)+1}'
        images.append(uri); entries.append(entry)
    if cfg['kind'] == 'image':
        if any(cfg.get(k) for k in ('first_frame','last_frame','audios','videos')):
            raise AgnesError('Image generation does not accept video/audio/keyframe fields.')
        if not payload.get('size'): raise AgnesError('Image size is required.')
        extra = payload.setdefault('extra_body',{})
        if 'image' in extra: raise AgnesError('Supply reference images through images/--image.')
        if images: extra['image'] = images
        response_format = cfg.get('response_format','url')
        if response_format not in {'url','b64_json'}: raise AgnesError('Invalid response_format.')
        extra['response_format'] = response_format
        if not images and response_format == 'b64_json': payload['return_base64'] = True
    else:
        if images: payload['images'] = images
        for field in ('first_frame','last_frame'):
            if cfg.get(field):
                payload[field], entry = image_input(cfg[field],origin,cfg.get('transport',{}))
                entry['slot'] = field; entries.append(entry)
        for field in ('audios','videos'):
            if cfg.get(field): payload[field] = cfg[field]
        for audio in payload.get('audios',[]): https_url(audio)
        for video in payload.get('videos',[]): https_url(video['url'])
        mode = payload.get('mode')
        if mode not in {'text','reference','keyframe'}: raise AgnesError('Video mode must be explicit.')
        frames = any(payload.get(k) for k in ('first_frame','last_frame'))
        refs = any(payload.get(k) for k in ('images','audios','videos'))
        if (mode == 'text' and (frames or refs)) or (mode == 'reference' and (frames or not refs)) or (mode == 'keyframe' and (not frames or refs)):
            raise AgnesError('Video mode and media fields conflict.')
        if 'seconds' in payload: payload['seconds'] = str(payload['seconds'])
        profiles = read_json(Path(__file__).resolve().parents[1]/'references'/'video-profiles.json')
        profile = profiles.get(cfg['model'])
        if profile:
            if payload.get('size') not in profile['sizes']: raise AgnesError('Unsupported model size.')
            try: seconds = int(payload.get('seconds',''))
            except ValueError: raise AgnesError('Integer seconds are required.') from None
            if not profile['min_seconds'] <= seconds <= profile['max_seconds']: raise AgnesError('Seconds outside model limits.')
            if payload.get('n',1) != 1: raise AgnesError('Video n must be 1.')
            if len(images) > profile['max_images'] or len(payload.get('audios',[])) > 3 or len(payload.get('videos',[])) > profile['max_videos']:
                raise AgnesError('Too many references for model.')
            if payload.get('aspect_ratio','16:9') not in profile['ratios']: raise AgnesError('Unsupported video ratio.')
        for entry in entries:
            if 'bytes' in entry and (entry['bytes'] >= 15*1024**2 or not all(256 <= entry[k] <= 5760 for k in ('width','height'))):
                raise AgnesError('Video reference image must be <15 MiB and dimensions 256..5760; configure transport resizing.')
    body = json.dumps(payload,ensure_ascii=False).encode('utf-8')
    if len(body) >= 50*1024**2: raise AgnesError('Request >=50 MiB; reduce transport dimensions or JPEG quality before submitting.')
    return payload, entries, body


def prepare(args):
    cfg,origin = load_config(args)
    payload,entries,body = build_payload(cfg,origin)
    preflight = dict(version=VERSION, kind=cfg['kind'],base_url=cfg['base_url'],
        request=safe(payload),references=safe(entries),request_bytes=len(body),request_sha256=digest(body),
        output_dir=cfg['output_dir'],output_name=cfg['output_name'])
    return cfg,payload,preflight


def key_for(state):
    key = os.getenv(state.get('api_key_env','AGNES_API_KEY'))
    if not key: raise AgnesError('API key environment variable is not configured.')
    return key


def state_path(args):
    if not args.run_dir: raise AgnesError('--run-dir is required.')
    return Path(args.run_dir).resolve()/'task.json'


def submit(args):
    cfg,payload,preflight = prepare(args)
    key = key_for(cfg)
    root = Path(cfg['output_dir'])
    state = {k:cfg[k] for k in ('kind','model','base_url','api_key_env','output_name','timeout','poll_interval','max_wait')}
    state.update(version=VERSION,status='submission_started',created_at=time.time(),request_sha256=preflight['request_sha256'])
    try: write_json(root/'task.json',state,exclusive=True)
    except FileExistsError: raise AgnesError('Task record exists. Resume status/wait/download; use a new output_dir only for a new generation.') from None
    write_json(root/'preflight.json',preflight)
    (root/'prompt.txt').write_text(cfg['prompt'],encoding='utf-8')
    endpoint = '/videos' if cfg['kind'] == 'video' else '/images/generations'
    try:
        result = api('POST',cfg['base_url']+endpoint,key,payload,cfg['timeout'])
        # Save before processing: recovery survives later downloads / validation failure.
        write_json(root/'response.json',result)
        if cfg['kind'] == 'video':
            if not result.get('video_id'): raise AgnesError('Create response lacks video_id; do not guess task_id or resubmit.')
            state.update(video_id=result['video_id'],status=result.get('status','queued'))
        else:
            if not result.get('data'): raise AgnesError('Image response lacks data; inspect saved response.')
            state['status'] = 'completed'
    except Exception as exc:
        state['status'] = 'submission_unknown'
        state['error'] = str(exc) if isinstance(exc,AgnesError) else type(exc).__name__
        write_json(root/'task.json',state)
        raise
    write_json(root/'task.json',state)
    print(json.dumps(safe(state),ensure_ascii=False))


def attach(args):
    if not args.video_id or not args.model: raise AgnesError('attach requires --video-id and --model.')
    state = dict(version=VERSION,kind='video',model=args.model,video_id=args.video_id,
        base_url=base_url(args.base_url or os.getenv('AGNES_BASE_URL') or DEFAULT_BASE),
        api_key_env=args.api_key_env or 'AGNES_API_KEY',output_name=args.output_name or 'result',
        timeout=args.timeout or 120,poll_interval=args.poll_interval or 30,max_wait=args.max_wait or 600,status='attached')
    if not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]+',state['output_name']) or state['output_name'] in {'.','..'}:
        raise AgnesError('Invalid output_name.')
    write_json(state_path(args),state,exclusive=True)
    print(json.dumps(safe(state),ensure_ascii=False))


def status(args, watch=False):
    path = state_path(args); state = read_json(path)
    if state['kind'] != 'video' or not state.get('video_id'):
        raise AgnesError('No known video_id; cannot poll or infer from task_id.')
    key = key_for(state)
    wait = args.max_wait if args.max_wait is not None else state['max_wait']
    interval = args.poll_interval if args.poll_interval is not None else state['poll_interval']
    timeout = args.timeout if args.timeout is not None else state['timeout']
    if min(wait,interval,timeout) <= 0: raise AgnesError('Timing options must be positive.')
    deadline = time.monotonic()+wait
    failures = 0
    url = base_url(state['base_url']).removesuffix('/v1')+'/agnesapi?'+urllib.parse.urlencode({'video_id':state['video_id'],'model_name':state['model']})
    while True:
        try:
            result = api('GET',url,key,timeout=min(timeout,max(0.1,deadline-time.monotonic())) if watch else timeout)
            write_json(path.parent/'result.json',result)
            state.update(status=result.get('status','unknown'),last_checked=time.time())
            write_json(path,state)
            print(json.dumps(safe({'video_id':state['video_id'],'status':state['status'],'progress':result.get('progress')}),ensure_ascii=False),flush=True)
            failures = 0
            delay = interval
            if state['status'] in TERMINAL: return 0 if state['status']=='completed' else 3
        except AgnesError as exc:
            if isinstance(exc,HTTPFailure) and exc.status not in RETRYABLE: raise
            if not watch: raise
            failures += 1
            delay = max(min(60,interval*2**min(failures-1,4)),getattr(exc,'retry_after',0))
            print(json.dumps({'status':'query_retry','reason':str(exc),'retry_in_seconds':delay}),flush=True)
        if not watch: return 0
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            print(json.dumps({'status':'wait_timeout','video_id':state['video_id'],'resume':'wait --run-dir '+str(path.parent)}),flush=True)
            return 4
        time.sleep(min(delay,remaining))
        if time.monotonic() >= deadline: return 4


def download(args):
    path = state_path(args); state = read_json(path); root = path.parent
    if state.get('status') != 'completed': raise AgnesError('Task is not completed; query it first.')
    result = read_json(root/('result.json' if state['kind']=='video' and (root/'result.json').exists() else 'response.json'))
    items = result.get('data',[]) if state['kind']=='image' else [{'url':(result.get('metadata') or {}).get('url') or result.get('url')}]
    if not items: raise AgnesError('Completed response has no output items.')
    saved = []
    for index,item in enumerate(items,1):
        raw = item.get('b64_json')
        if raw:
            try: data = base64.b64decode(raw.split(',',1)[-1] if raw.startswith('data:') else raw,validate=True)
            except ValueError: raise AgnesError('Invalid output Base64.') from None
        elif item.get('url'):
            # Deliberately do not forward the API Authorization header to asset hosts.
            url = https_url(item['url'])
            with urllib.request.urlopen(url,timeout=args.timeout or state['timeout']) as response:
                https_url(response.geturl())
                data = response.read()
        else: raise AgnesError('Output item has no URL or Base64.')
        if not data: raise AgnesError('Empty output asset.')
        if state['kind']=='image':
            from PIL import Image
            with Image.open(io.BytesIO(data)) as im:
                im.verify()
                ext = {'PNG':'.png','JPEG':'.jpg','WEBP':'.webp'}.get(im.format)
                if not ext: raise AgnesError('Unsupported returned image format.')
        else:
            if b'ftyp' not in data[:64]: raise AgnesError('Downloaded video is not an MP4 container.')
            ext = '.mp4'
        filename = state['output_name']+(f'-{index:02}' if len(items)>1 else '')+ext
        dest = root/filename
        if dest.exists():
            if digest(dest.read_bytes()) != digest(data): raise AgnesError('Refusing to overwrite different output: '+filename)
        else:
            with dest.open('xb') as f: f.write(data)
        saved.append({'path':str(dest),'bytes':len(data),'sha256':digest(data)})
    write_json(root/'downloads.json',saved)
    print(json.dumps(saved,ensure_ascii=False))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',action='version',version=VERSION)
    subs = p.add_subparsers(dest='command',required=True)
    for command in ('plan','submit','attach','status','wait','download'):
        s = subs.add_parser(command)
        s.add_argument('--timeout',type=float)
        if command in ('plan','submit'):
            s.add_argument('--config'); s.add_argument('--kind',choices=['image','video'])
            s.add_argument('--model'); s.add_argument('--prompt'); s.add_argument('--prompt-file')
            s.add_argument('--image',action='append',help='Repeat in reference order; replaces config image array.')
            s.add_argument('--first-frame'); s.add_argument('--last-frame')
            s.add_argument('--output-dir'); s.add_argument('--output-name')
            s.add_argument('--base-url'); s.add_argument('--api-key-env')
            s.add_argument('--parameters-json'); s.add_argument('--seconds')
            s.add_argument('--size'); s.add_argument('--aspect-ratio'); s.add_argument('--mode')
            s.add_argument('--seed',type=int); s.add_argument('--response-format',choices=['url','b64_json'])
            s.add_argument('--max-edge',type=int); s.add_argument('--image-format',choices=['original','png','jpeg','webp'])
            s.add_argument('--jpeg-quality',type=int)
            s.add_argument('--poll-interval',type=float); s.add_argument('--max-wait',type=float)
        else:
            s.add_argument('--run-dir',required=True)
            if command in ('attach','status','wait'):
                s.add_argument('--poll-interval',type=float); s.add_argument('--max-wait',type=float)
            if command == 'attach':
                s.add_argument('--video-id',required=True); s.add_argument('--model',required=True)
                s.add_argument('--base-url'); s.add_argument('--api-key-env'); s.add_argument('--output-name')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'plan':
            cfg,_,preflight = prepare(args)
            write_json(Path(cfg['output_dir'])/'plan.json',preflight)
            print(json.dumps(preflight,ensure_ascii=False,indent=2))
        elif args.command == 'submit': submit(args)
        elif args.command == 'attach': attach(args)
        elif args.command in ('status','wait'): return status(args,args.command=='wait')
        elif args.command == 'download': download(args)
        return 0
    except (AgnesError,OSError,ValueError,KeyError,ImportError) as exc:
        message = str(exc) if isinstance(exc,AgnesError) else f'{type(exc).__name__}: check configuration, files and dependencies.'
        print(json.dumps({'error':message},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
