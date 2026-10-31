"""Selection, recovery and scaffold behavior in isolated temporary directories."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from render_episode_review import render


class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict]] = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.elements.append((tag, dict(attrs)))


class ReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix='漫剧 审阅测试 ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = self.root / '制作审阅' / '素材清单.json'
        self.manifest.parent.mkdir()

    def write(self, items: list[dict], **extra: object) -> None:
        self.manifest.write_text(json.dumps({'title': '另一题材 · 古装探案', 'review_mode': 'materials', 'items': items, **extra}, ensure_ascii=False), encoding='utf-8')

    def item(self, filename: str, version: str, **extra: object) -> dict:
        (self.root / filename).write_bytes(b'fixture')
        return {'id': '同一道具', 'category': 'images', 'version': version, 'current': True, 'status': '待审', 'path': '../' + filename, **extra}

    def test_related_review_page_link_is_visible_and_validated(self) -> None:
        target = self.manifest.parent / '参考审核.html'
        target.write_text('ok', encoding='utf-8')
        self.write([], related_pages=[{'label': '参考审核', 'path': target.name}])
        output = render(self.manifest)
        self.assertIn('参考审核', output.read_text(encoding='utf-8'))
        before = output.read_bytes()
        self.write([], related_pages=[{'label': '缺失', 'path': 'missing.html'}])
        with self.assertRaisesRegex(ValueError, '不存在'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), before)

    def test_video_exposes_declared_inputs_and_rejects_missing_reference(self) -> None:
        video = self.item('片段.mp4', 'v001')
        video['category'] = 'video'
        ref = self.item('眼部参考.png', 'v001')
        video['input_references'] = [{'kind': 'image', 'path': ref['path'],
                                      'label': '图片1', 'role': '眼部', 'sha256': 'example'}]
        self.write([video])
        output = render(self.manifest)
        text = output.read_text(encoding='utf-8')
        page = Page(text)
        self.assertIn('查看本镜实际绑定的参考图与音色', text)
        self.assertTrue(any(tag == 'img' and '%E7%9C%BC%E9%83%A8' in attrs['src'] for tag, attrs in page.elements))
        before = output.read_bytes()
        video['input_references'][0]['path'] = '../missing.png'
        self.write([video])
        with self.assertRaisesRegex(ValueError, '不存在'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), before)

    def test_replace_without_deleting_evidence_and_hide_empty_categories(self) -> None:
        old = self.item('票券 旧版.png', 'v001', current=False, status='已退回')
        new = self.item('票券 新版.png', 'v002')
        self.write([old, new])
        page = Page(render(self.manifest).read_text(encoding='utf-8'))
        images = [attrs['src'] for tag, attrs in page.elements if tag == 'img']
        sections = [attrs.get('id') for tag, attrs in page.elements if tag == 'section']
        self.assertEqual(len(images), 1)
        self.assertIn('%E6%96%B0%E7%89%88', images[0])
        self.assertNotIn('audio', sections)
        self.assertTrue((self.root / '票券 旧版.png').is_file())
        self.assertTrue(any(tag == 'button' and 'data-copy' in attrs for tag, attrs in page.elements))
        ids = [attrs['id'] for _, attrs in page.elements if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicate_selection_or_missing_source_preserves_old_page(self) -> None:
        item = self.item('当前.png', 'v001')
        self.write([item])
        output = render(self.manifest)
        previous = output.read_bytes()
        self.write([item, {**item, 'version': 'v002'}])
        with self.assertRaisesRegex(ValueError, '多个当前版本'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), previous)
        self.write([{**item, 'path': '../不存在.png'}])
        with self.assertRaisesRegex(ValueError, '不存在'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), previous)

    def test_rejected_current_has_no_media_and_task_is_escaped(self) -> None:
        item = self.item('废稿.png', 'v001', status='已退回')
        self.write([item], tasks=[{'name': '<script>alert(1)</script>', 'status': '生成中'}])
        text = render(self.manifest).read_text(encoding='utf-8')
        self.assertNotIn('<img ', text)
        self.assertNotIn('<script>alert(1)</script>', text)
        self.assertIn('&lt;script&gt;', text)

    def test_script_text_is_not_template_or_executable_markup(self) -> None:
        source = self.root / '剧本.txt'
        source.write_text('<script>alert(1)</script> @@NAV@@ 中文对白', encoding='utf-8')
        self.write([{'id': '正稿', 'category': 'script', 'version': 'v003', 'current': True, 'status': '待审', 'path': '../剧本.txt'}])
        text = render(self.manifest).read_text(encoding='utf-8')
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt; @@NAV@@ 中文对白', text)

    def test_scaffold_is_reentrant_without_overwriting_user_review(self) -> None:
        script = Path(__file__).with_name('scaffold_manju.py')
        command = [sys.executable, '-B', '-X', 'utf8', str(script), 'episodes', '06', '--season', str(self.root / '剧集')]
        subprocess.run(command, check=True, capture_output=True, timeout=20)
        folder = self.root / '剧集/06/制作审阅'
        manifest, page = folder / '素材清单.json', folder / '本集制作总览.html'
        manifest.write_text('{"items": [], "title": "用户已改名"}', encoding='utf-8')
        page.write_text('用户自定义页面', encoding='utf-8')
        subprocess.run(command, check=True, capture_output=True, timeout=20)
        self.assertEqual(json.loads(manifest.read_text(encoding='utf-8'))['title'], '用户已改名')
        self.assertEqual(page.read_text(encoding='utf-8'), '用户自定义页面')

    def test_all_categories_render_without_autoplay_and_protect_source(self) -> None:
        items = []
        for category, suffix in [('script', '.txt'), ('images', '.png'), ('audio', '.wav'), ('video', '.mp4'), ('sfx', '.wav'), ('music', '.wav'), ('final', '.mp4')]:
            source = self.root / (category + suffix)
            source.write_text('测试素材', encoding='utf-8')
            items.append({'id': category, 'category': category, 'version': 'v001', 'current': True, 'status': '待审', 'path': '../' + source.name})
        self.write(items)
        page = Page(render(self.manifest).read_text(encoding='utf-8'))
        sections = {attrs.get('id') for tag, attrs in page.elements if tag == 'section'}
        self.assertEqual(sections, {item['category'] for item in items})
        players = [attrs for tag, attrs in page.elements if tag in ('audio', 'video')]
        self.assertEqual(len(players), 5)
        self.assertTrue(all(attrs.get('preload') == 'none' and 'autoplay' not in attrs for attrs in players))
        # An HTML script source can be displayed, but never overwritten by the overview.
        protected = self.root / '剧本.html'
        protected.write_text('原剧本', encoding='utf-8')
        self.write([{'id': '剧本', 'category': 'script', 'version': 'v001', 'current': True, 'status': '待审', 'path': '../剧本.html'}])
        with self.assertRaisesRegex(ValueError, '不能覆盖当前素材'):
            render(self.manifest, protected)
        self.assertEqual(protected.read_text(encoding='utf-8'), '原剧本')

    def test_default_complete_shows_only_new_full_cut(self) -> None:
        old = self.item('旧整集.mp4', 'v001', id='旧整集', category='final', status='历史粗剪，用户已退回')
        new = self.item('新整集.mp4', 'v002', id='当前整集', category='final')
        clip = self.item('生成片段.mp4', 'v002', id='镜头01', category='video')
        self.write([old, new, clip], review_mode='complete')
        data = json.loads(self.manifest.read_text(encoding='utf-8'))
        data.pop('review_mode')
        self.manifest.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        page = Page(render(self.manifest).read_text(encoding='utf-8'))
        players = [attrs for tag, attrs in page.elements if tag == 'video']
        self.assertEqual(len(players), 1)
        self.assertIn('%E6%96%B0%E6%95%B4%E9%9B%86', players[0]['src'])
        checkbox = next(attrs for tag, attrs in page.elements if attrs.get('id') == 'auto-refresh')
        self.assertNotIn('checked', checkbox)
        self.assertTrue((self.root / '旧整集.mp4').exists())

    def test_stale_complete_cut_is_hidden_until_new_export(self) -> None:
        old = self.item('原整集.mp4', 'v003', category='final', stale=True)
        self.write([old], review_mode='complete', tasks=[{'name':'新整集','status':'重新导出中'}])
        text = render(self.manifest).read_text(encoding='utf-8')
        self.assertNotIn('<video ', text)
        self.assertIn('重新导出中', text)
        self.assertIn('最新完整候选正在制作或导出', text)

    def test_multiple_complete_candidates_do_not_replace_existing_page(self) -> None:
        first = self.item('整集甲.mp4', 'v001', category='final', id='甲')
        second = self.item('整集乙.mp4', 'v002', category='final', id='乙')
        self.write([first], review_mode='complete')
        output = render(self.manifest)
        previous = output.read_bytes()
        self.write([first, second], review_mode='complete')
        with self.assertRaisesRegex(ValueError, '一个当前完整候选'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), previous)


    def test_complete_cut_adoption_is_explicit_collapsed_and_bound_to_final(self) -> None:
        final = self.item('整集.mp4', 'v010', id='整集', category='final', sha256='final-hash')
        used = self.item('采用源片.mp4', 'v003', id='采用', category='video')
        unused = self.item('未采用源片.mp4', 'v009', id='未采用', category='video')
        reference = self.item('本镜参考.png', 'v003', id='参考')
        adoption = {'version':'v010', 'final_sha256':'final-hash', 'fps':24,
                    'clips':[{'id':'采用', 'source_video':{'path':used['path']},
                              'reference':{'path':reference['path']},
                              'timeline_frame_range':[0,48], 'source_frame_range':[12,60]}], 'assets':[]}
        self.write([final,used,unused,reference], review_mode='complete', adoption=adoption)
        text = render(self.manifest).read_text(encoding='utf-8')
        page = Page(text)
        self.assertIn('00:00.000—00:02.000',text)
        self.assertIn('源帧 [12, 60)',text)
        self.assertIn('%E9%87%87%E7%94%A8%E6%BA%90%E7%89%87',text)
        self.assertNotIn('%E6%9C%AA%E9%87%87%E7%94%A8',text)
        self.assertLess(text.index('id="final"'),text.index('id="adoption"'))
        toggles = [attrs for tag,attrs in page.elements if tag=='details' and attrs.get('class')=='adoption-list']
        self.assertEqual(len(toggles),2)
        self.assertTrue(all('open' not in attrs for attrs in toggles))
        self.assertTrue(all(attrs.get('preload')=='none' and 'autoplay' not in attrs
                            for tag,attrs in page.elements if tag in ('video','audio')))
        output = self.manifest.parent/'本集制作总览.html'
        original = output.read_bytes()
        adoption['final_sha256']='wrong-cut'
        self.write([final],review_mode='complete',adoption=adoption)
        with self.assertRaisesRegex(ValueError,'版本或指纹不符'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(),original)
        adoption['final_sha256']='final-hash'
        adoption['clips'][0]['reference']['path']='../缺失参考.png'
        self.write([final],review_mode='complete',adoption=adoption)
        with self.assertRaisesRegex(ValueError,'不存在'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(),original)


    def test_adoption_keeps_all_bound_media_and_rejects_missing_later_input(self) -> None:
        final = self.item('整集.mp4', 'v011', id='整集', category='final', sha256='cut')
        source = self.item('源片.mp4', 'v001', id='源片', category='video')
        refs = []
        for kind, filename in [('image','全身.png'),('image','构图.png'),('audio','音色.wav'),('video','动作.mp4')]:
            asset = self.item(filename, 'v001')
            refs.append({'kind':kind, 'path':asset['path'], 'label':filename, 'sha256':'input-hash'})
        adoption = {'version':'v011','final_sha256':'cut','fps':24,'assets':[],
                    'clips':[{'id':'镜头','source_video':{'path':source['path']},
                              'source_frame_range':[0,48],'timeline_frame_range':[0,48],
                              'input_references':refs}]}
        self.write([final], review_mode='complete', adoption=adoption)
        output = render(self.manifest)
        previous = output.read_bytes()
        page = Page(previous.decode('utf-8'))
        kinds = [attrs['data-reference-kind'] for _,attrs in page.elements if 'data-reference-kind' in attrs]
        self.assertEqual(kinds, ['image','image','audio','video'])
        self.assertEqual(sum(tag=='audio' for tag,_ in page.elements), 1)
        self.assertEqual(sum(tag=='video' for tag,_ in page.elements), 3)
        refs[1]['path']='../不存在的第二张.png'
        self.write([final], review_mode='complete', adoption=adoption)
        with self.assertRaisesRegex(ValueError, '不存在'):
            render(self.manifest)
        self.assertEqual(output.read_bytes(), previous)

if __name__ == '__main__':
    unittest.main()
