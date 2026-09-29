(function () {
  var KEY = 'sd_collect';
  var store = {}; try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
  var n = Object.keys(store).length;
  if (!n) { alert('모아 둔 제품이 없습니다'); return; }
  if (confirm(n + '개를 브라우저에서 지울까요? 아직 내보내지 않았다면 취소를 누르세요')) { localStorage.removeItem(KEY); alert('비웠습니다'); }
})();
