"""Offline behavioral tests. Never calls Agnes or uses a real key."""
import base64
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
import agnes_generate as app


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'中文 目录'
        self.root.mkdir()
        (self.root/'提示词.txt').write_text('\ufeff保持角色和宝剑',encoding='utf-8')
        for i in range(4): Image.new('RGB',(512,768),(i*50,10,20)).save(self.root/f'{i}.png')
        self.cfg = dict(kind='video',model='agnes-video-2.5-flash',prompt_file='提示词.txt',
            output_dir='输出',parameters=dict(mode='reference',seconds=12,size='720P',aspect_ratio='16:9'),
            images=[f'{i}.png' for i in range(4)],transport=dict(format='jpeg',max_edge=640,quality=94))
        self.conf = self.root/'任务.json'

    def args(self, command='plan', *rest):
        app.write_json(self.conf,self.cfg)
        return app.parser().parse_args([command,'--config',str(self.conf),*rest])

    def run_args(self, command):
        return app.parser().parse_args([command,'--run-dir',str(self.root/'输出')])

    def submit(self, response):
        with patch.dict(os.environ,{'AGNES_API_KEY':'fake-test-key'}), patch.object(app,'api',return_value=response), contextlib.redirect_stdout(io.StringIO()):
            app.submit(self.args('submit'))

    def test_chinese_relative_paths_and_reference_order(self):
        cfg,payload,plan = app.prepare(self.args())
        self.assertEqual(cfg['prompt'],'保持角色和宝剑')
        self.assertEqual(payload['seconds'],'12')
        self.assertEqual([Path(e['source']).name for e in plan['references']],[f'{i}.png' for i in range(4)])
        self.assertTrue(all(x.startswith('data:image/jpeg;base64,') for x in payload['images']))
        self.assertEqual(plan['references'][0]['height'],640)
        self.assertNotIn('base64,',json.dumps(plan))
        with Image.open(self.root/'0.png') as original:
            self.assertEqual(original.size,(512,768))

    def test_cli_overrides_config(self):
        cfg,payload,_ = app.prepare(self.args('plan','--prompt','新提示','--seconds','6','--image',str(self.root/'3.png')))
        self.assertEqual(payload['prompt'],'新提示')
        self.assertEqual(payload['seconds'],'6')
        self.assertEqual(len(payload['images']),1)

    def test_plan_offline_without_key(self):
        self.args()
        with patch.dict(os.environ,{},clear=True), patch.object(app,'api') as api, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.main(['plan','--config',str(self.conf)]),0)
        api.assert_not_called()
        self.assertFalse((self.root/'输出'/'task.json').exists())

    def test_image_extra_body_contract(self):
        self.cfg.update(kind='image',model='agnes-image-2.1-flash',parameters={'size':'2K','ratio':'16:9'},response_format='b64_json')
        _,payload,_ = app.prepare(self.args())
        self.assertEqual(len(payload['extra_body']['image']),4)
        self.assertEqual(payload['extra_body']['response_format'],'b64_json')
        self.assertNotIn('images',payload)
        self.assertNotIn('response_format',payload)

    def test_text_image_base64_flag(self):
        self.cfg.update(kind='image',model='agnes-image-2.1-flash',parameters={'size':'1K'},images=[],response_format='b64_json')
        self.assertTrue(app.prepare(self.args())[1]['return_base64'])

    def test_keyframe_and_conflicting_mode(self):
        self.cfg.update(images=[],first_frame='0.png')
        self.cfg['parameters']['mode']='keyframe'
        self.assertIn('first_frame',app.prepare(self.args())[1])
        self.cfg['images']=['1.png']
        with self.assertRaises(app.AgnesError): app.prepare(self.args())

    def test_flash_limits(self):
        self.cfg['parameters']['size']='1080P'
        with self.assertRaises(app.AgnesError): app.prepare(self.args())
        self.cfg['parameters']['size']='720P'
        self.cfg['parameters']['seconds']=13
        with self.assertRaises(app.AgnesError): app.prepare(self.args())
        self.cfg['parameters']['seconds']=12
        self.cfg['images']=['0.png']*6
        with self.assertRaises(app.AgnesError): app.prepare(self.args())

    def test_transparency_original_preserved(self):
        path = self.root/'alpha.png'
        Image.new('RGBA',(512,512),(0,0,0,0)).save(path)
        uri,_=app.image_input(str(path),self.root,{})
        self.assertEqual(base64.b64decode(uri.split(',')[1]),path.read_bytes())

    def test_submit_once_then_resume(self):
        self.submit({'video_id':'known-id','status':'queued'})
        with patch.dict(os.environ,{'AGNES_API_KEY':'fake-test-key'}), patch.object(app,'api') as api:
            with self.assertRaises(app.AgnesError): app.submit(self.args('submit'))
            api.assert_not_called()

    def test_unknown_submission_never_reposts(self):
        with patch.dict(os.environ,{'AGNES_API_KEY':'fake-test-key'}), patch.object(app,'api',side_effect=app.AgnesError('timeout')) as api:
            with self.assertRaises(app.AgnesError): app.submit(self.args('submit'))
            self.assertEqual(api.call_count,1)
            self.assertEqual(app.read_json(self.root/'输出'/'task.json')['status'],'submission_unknown')
            with self.assertRaises(app.AgnesError): app.submit(self.args('submit'))
            self.assertEqual(api.call_count,1)

    def test_missing_video_id_does_not_guess(self):
        with self.assertRaises(app.AgnesError): self.submit({'task_id':'not-a-video-id','status':'queued'})
        self.assertNotIn('video_id',app.read_json(self.root/'输出'/'task.json'))

    def test_read_retry_uses_same_endpoint_and_id(self):
        self.submit({'video_id':'known-id','status':'queued'})
        with patch.dict(os.environ,{'AGNES_API_KEY':'fake-test-key'}), patch.object(app,'api',side_effect=[app.HTTPFailure(429),{'status':'completed','url':'https://assets.example/video.mp4'}]) as api, patch.object(app.time,'sleep'), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(app.status(self.run_args('wait'),True),0)
            self.assertEqual(api.call_count,2)
            for call in api.call_args_list:
                self.assertEqual(call.args[0],'GET')
                self.assertIn('video_id=known-id&model_name=agnes-video-2.5-flash',call.args[1])

    def test_auth_failure_not_retried(self):
        self.submit({'video_id':'known-id','status':'queued'})
        with patch.dict(os.environ,{'AGNES_API_KEY':'fake-test-key'}), patch.object(app,'api',side_effect=app.HTTPFailure(401)) as api:
            with self.assertRaises(app.HTTPFailure): app.status(self.run_args('wait'),True)
            self.assertEqual(api.call_count,1)

    def test_download_base64_image_and_no_overwrite(self):
        self.cfg.update(kind='image',model='agnes-image-2.1-flash',parameters={'size':'1K'},images=[])
        raw=(self.root/'0.png').read_bytes()
        self.submit({'data':[{'b64_json':base64.b64encode(raw).decode()}]})
        with contextlib.redirect_stdout(io.StringIO()): app.download(self.run_args('download'))
        dest=self.root/'输出'/'result.png'
        self.assertEqual(dest.read_bytes(),raw)
        dest.write_bytes(b'existing different file')
        with self.assertRaises(app.AgnesError): app.download(self.run_args('download'))
        self.assertEqual(dest.read_bytes(),b'existing different file')

    def test_download_metadata_and_no_bearer(self):
        self.submit({'video_id':'known-id','status':'completed','metadata':{'url':'https://assets.example/v.mp4'}})
        data=b'\x00\x00\x00\x18ftypmp42'+b'0'*30
        response=io.BytesIO(data)
        response.geturl=lambda: 'https://assets.example/v.mp4'
        with patch.object(app.urllib.request,'urlopen',return_value=response) as op, contextlib.redirect_stdout(io.StringIO()):
            app.download(self.run_args('download'))
            self.assertIsInstance(op.call_args.args[0],str)
            self.assertNotIn('Authorization',str(op.call_args))
        self.assertEqual((self.root/'输出'/'result.mp4').read_bytes(),data)

    def test_redirect_and_bad_destinations(self):
        for url in ['http://host/v1','https://user:password@host/v1','https://host/v1?token=x']:
            with self.assertRaises(app.AgnesError): app.base_url(url)
        with self.assertRaises(app.AgnesError): app.NoRedirect().redirect_request(None,None,302,'',{},'https://another.host/')
        self.cfg['output_name']='../elsewhere'
        with self.assertRaises(app.AgnesError): app.prepare(self.args())

    def test_attach_does_not_generate(self):
        args=app.parser().parse_args(['attach','--run-dir',str(self.root/'attached'),'--video-id','already-known','--model','agnes-video-2.5-flash'])
        with patch.object(app,'api') as api,contextlib.redirect_stdout(io.StringIO()): app.attach(args)
        api.assert_not_called()
        self.assertEqual(app.read_json(self.root/'attached'/'task.json')['video_id'],'already-known')


if __name__=='__main__': unittest.main()
