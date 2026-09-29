(function () {
  var KEY = 'sd_collect';
  function toast(msg, ok) {
    var el = document.getElementById('sd-toast');
    if (!el) { el = document.createElement('div'); el.id = 'sd-toast'; document.body.appendChild(el); }
    el.setAttribute('style', 'position:fixed;top:12px;right:12px;z-index:2147483647;padding:10px 14px;border-radius:8px;font:14px/1.4 sans-serif;color:#fff;background:' + (ok ? '#2e7d32' : '#c62828') + ';box-shadow:0 4px 12px rgba(0,0,0,.25)');
    el.textContent = msg;
    clearTimeout(el._t); el._t = setTimeout(function () { el.remove(); }, 3500);
  }
  var node = document.getElementById('__NEXT_DATA__');
  if (!node) { toast('이 페이지에는 데이터가 없습니다. 제품 페이지에서 눌러 주세요', false); return; }
  var data; try { data = JSON.parse(node.textContent); } catch (e) { toast('페이지 데이터를 읽지 못했습니다', false); return; }
  var pp = (data.props && data.props.pageProps) || {};
  var info = pp.productIngredientInfoData || {};
  var list = info.ingredients || [];
  if (!list.length) { toast('전성분이 없는 페이지입니다', false); return; }
  var pid = null;
  try { pid = pp.productReviewSummaryData.productMetaData.productIndex; } catch (e) {}
  if (!pid) { var m = JSON.stringify(pp).match(/"(?:productIndex|product_id)":\s*(\d+)/); if (m) pid = Number(m[1]); }
  var gm = location.pathname.match(/\/goods\/(?:[^\/]+\/)?(\d+)/); var gid = gm ? Number(gm[1]) : null;
  var pm = location.pathname.match(/\/products\/(\d+)/); if (!pid && pm) pid = Number(pm[1]);
  var rec = {
    product_id: pid, goods_id: gid, url: location.href, title: document.title,
    collected_at: new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().replace('Z', '+09:00'),
    ingredients: list.map(function (i) { return { id: i.id, korean: i.korean, english: i.english, ewg: i.ewg, purposes: i.purposes || [] }; })
  };
  var store = {}; try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { store = {}; }
  var k = pid ? String(pid) : (gid ? 'goods_' + gid : location.href);
  var dup = !!store[k];
  store[k] = rec;
  localStorage.setItem(KEY, JSON.stringify(store));
  toast((dup ? '다시 저장 ' : '저장 ') + Object.keys(store).length + '개 (성분 ' + list.length + '개, 제품 ' + (pid || '번호 없음') + ')', true);
})();
