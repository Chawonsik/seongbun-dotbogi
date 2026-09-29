(function () {
  var KEY = 'sd_collect';
  var store = {}; try { store = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
  var n = Object.keys(store).length;
  if (!n) { alert('모아 둔 제품이 없습니다'); return; }
  var d = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16).replace(/[-:T]/g, '').replace(/(\d{8})(\d{4})/, '$1-$2');
  var payload = { exported_at: new Date().toISOString(), count: n, records: store };
  var blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
  var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'sd-collect-' + d + '.json';
  document.body.appendChild(a); a.click(); a.remove();
  if (confirm(n + '개를 내보냈습니다. 브라우저에 모아 둔 것을 비울까요? (파일을 확인한 뒤 비우려면 취소)')) { localStorage.removeItem(KEY); }
})();
