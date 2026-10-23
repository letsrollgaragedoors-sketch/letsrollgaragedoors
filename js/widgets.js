/* Let's Roll Garage Doors: October coupon pop-up + floating chat widget.
   Loaded with defer on every page. Styles are injected here so no extra CSS request blocks rendering. */
(function () {
  'use strict';

  var TEL = 'tel:+15129474451';
  var PHONE = '(512) 947-4451';
  var ACCESS_KEY = '04548151-caf0-4166-b696-19dafbd20e6e'; // same Web3Forms key as the quote form
  var SEND_TO_EMAIL = true; // set to false to only console.log leads
  var DEALS_END = new Date('2026-11-01T00:00:00-05:00').getTime(); // deals run through Oct 31, 2026
  var DEALS_LIVE = Date.now() < DEALS_END;
  var POPUP_DELAY = 6000;
  var TEASER_DELAY = 5000;
  var TEASER_HIDE = 8000;

  function store(get, k, v) {
    try { return get ? sessionStorage.getItem(k) : sessionStorage.setItem(k, v); } catch (e) { return null; }
  }

  function sendLead(type, fields) {
    var data = { type: type, page: location.pathname, time: new Date().toISOString() };
    for (var k in fields) data[k] = fields[k];
    console.log('[Lead]', data);
    if (!SEND_TO_EMAIL) return;
    try {
      var fd = new FormData();
      fd.append('access_key', ACCESS_KEY);
      fd.append('subject', 'Website lead (' + type + '): ' + (fields.name || ''));
      fd.append('from_name', "Let's Roll Website");
      fd.append('botcheck', '');
      for (var f in data) fd.append(f, data[f]);
      fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { Accept: 'application/json' }, body: fd }).catch(function () {});
    } catch (e) {}
  }

  var css = '' +
    '.lr-pop{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(10,14,24,.72);opacity:0;transition:opacity .25s ease}' +
    '.lr-pop[hidden]{display:none}.lr-pop.lr-show{opacity:1}' +
    '.lr-pop-card{position:relative;width:100%;max-width:400px;max-height:calc(100vh - 32px);overflow:auto;background:#fff;border-radius:18px;box-shadow:0 24px 70px rgba(0,0,0,.45);font-family:"Open Sans",sans-serif;color:#1d1d1f;transform:translateY(14px) scale(.98);transition:transform .25s ease}' +
    '.lr-show .lr-pop-card{transform:none}' +
    '.lr-pop-head{background:var(--navy,#132a52);color:#fff;text-align:center;padding:30px 24px 22px}' +
    '.lr-pop-badge{display:inline-block;background:var(--gold,#c9962c);color:#1a1a1a;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:4px 12px;border-radius:99px;margin-bottom:12px}' +
    '.lr-pop-amt{font-family:Oswald,sans-serif;font-size:40px;font-weight:700;line-height:1.05;color:var(--orange-light,#ff8a3d)}' +
    '.lr-pop-sub{font-size:15px;margin-top:6px;opacity:.92}' +
    '.lr-x{position:absolute;top:8px;right:10px;width:34px;height:34px;border:0;border-radius:50%;background:rgba(255,255,255,.14);color:#fff;font-size:22px;line-height:1;cursor:pointer}' +
    '.lr-x:hover{background:rgba(255,255,255,.28)}' +
    '.lr-pop-body{padding:22px 24px 8px}' +
    '.lr-pop-body p{margin:0 0 14px;font-size:15px;line-height:1.5;color:#444}' +
    '.lr-field{display:block;width:100%;box-sizing:border-box;margin:0 0 12px;padding:13px 14px;font:inherit;font-size:16px;border:1.5px solid #d6d6da;border-radius:10px;background:#fff;color:#1d1d1f}' +
    '.lr-field:focus{outline:none;border-color:var(--orange,#c24c07);box-shadow:0 0 0 3px rgba(194,76,7,.18)}' +
    'textarea.lr-field{resize:vertical;min-height:70px}' +
    '.lr-btn{display:block;width:100%;box-sizing:border-box;text-align:center;text-decoration:none;border:0;border-radius:12px;background:var(--orange,#c24c07);color:#fff;font-family:Oswald,sans-serif;font-size:17px;font-weight:600;letter-spacing:.02em;padding:14px 18px;cursor:pointer}' +
    '.lr-btn:hover{background:var(--orange-dark,#9c3e05)}.lr-btn[disabled]{opacity:.6;cursor:default}' +
    '.lr-link{display:block;width:100%;margin:12px 0 4px;border:0;background:none;color:#6e6e73;font:inherit;font-size:13px;text-decoration:underline;cursor:pointer;text-align:center}' +
    '.lr-pop-foot{background:#fff6ee;color:var(--orange-dark,#9c3e05);text-align:center;font-size:12.5px;font-weight:700;padding:11px 14px;margin-top:10px;border-top:1px solid #f1dfcf}' +
    '.lr-code{border:2px dashed var(--orange,#c24c07);border-radius:12px;text-align:center;padding:12px;margin:4px 0 16px}' +
    '.lr-code small{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#6e6e73}' +
    '.lr-code strong{font-family:Oswald,sans-serif;font-size:28px;letter-spacing:.14em;color:var(--orange-dark,#9c3e05)}' +
    '.lr-err{color:#b3261e;font-size:13px;margin:-6px 0 10px;display:none}' +
    /* chat */
    '.lr-chat-btn{position:fixed;right:16px;bottom:90px;z-index:9998;width:60px;height:60px;border:0;border-radius:50%;background:var(--orange,#c24c07);color:#fff;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.3);display:flex;align-items:center;justify-content:center;transition:transform .15s ease}' +
    '.lr-chat-btn:hover{transform:scale(1.06)}.lr-chat-btn svg{width:28px;height:28px;fill:#fff}' +
    '.lr-dot{position:absolute;top:4px;right:4px;width:13px;height:13px;border-radius:50%;background:#22c55e;border:2px solid #fff;animation:lrPulse 1.8s infinite}' +
    '@keyframes lrPulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 9px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}' +
    '.lr-teaser{position:fixed;right:16px;bottom:160px;z-index:9998;max-width:240px;background:#fff;color:#1d1d1f;font:600 14px/1.4 "Open Sans",sans-serif;padding:12px 14px;border-radius:14px 14px 4px 14px;box-shadow:0 8px 28px rgba(0,0,0,.25);display:none;cursor:pointer}' +
    '.lr-teaser.lr-on{display:block;animation:lrIn .3s ease}@keyframes lrIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}' +
    '.lr-panel{position:fixed;right:16px;bottom:160px;z-index:9999;width:360px;max-width:calc(100vw - 24px);max-height:calc(100vh - 180px);display:none;flex-direction:column;background:#fff;border-radius:16px;box-shadow:0 18px 60px rgba(0,0,0,.35);overflow:hidden;font-family:"Open Sans",sans-serif;color:#1d1d1f}' +
    '.lr-panel.lr-open{display:flex}' +
    '.lr-panel-head{background:var(--navy,#132a52);color:#fff;padding:16px 18px;position:relative}' +
    '.lr-panel-head strong{display:block;font-family:Oswald,sans-serif;font-size:18px;letter-spacing:.01em}' +
    '.lr-panel-head span{font-size:13px;opacity:.9}' +
    '.lr-panel-head .lr-x{top:12px;right:12px}' +
    '.lr-panel-body{padding:16px 16px 14px;overflow:auto;background:#f6f7f9}' +
    '.lr-msg{background:#fff;border-radius:14px 14px 14px 4px;padding:11px 13px;margin:0 0 10px;font-size:14.5px;line-height:1.5;max-width:92%;box-shadow:0 1px 2px rgba(0,0,0,.06)}' +
    '.lr-msg a{color:var(--orange,#c24c07);font-weight:700}' +
    '.lr-panel form{margin-top:14px}' +
    '.lr-thanks{text-align:center;padding:10px 4px}.lr-thanks h3{font-family:Oswald,sans-serif;font-size:22px;margin:0 0 8px}' +
    '.lr-thanks p{font-size:14.5px;color:#444;margin:0 0 14px}' +
    '@media(max-width:480px){.lr-panel{right:8px;left:8px;width:auto;max-width:none;bottom:150px;max-height:calc(100vh - 170px)}.lr-teaser{right:12px}.lr-chat-btn{right:12px}}' +
    '@media(prefers-reduced-motion:reduce){.lr-dot{animation:none}.lr-pop,.lr-pop-card{transition:none}}';

  function el(html) {
    var d = document.createElement('div');
    d.innerHTML = html.trim();
    return d.firstChild;
  }

  function init() {
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);

    /* ---------- chat widget ---------- */
    var deals = DEALS_LIVE
      ? '<div class="lr-msg">🎟️ Ask about our October specials: up to $79 off spring repairs!</div>'
      : '';
    var chatBtn = el('<button type="button" class="lr-chat-btn" aria-label="Open chat" aria-expanded="false" aria-controls="lr-panel">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3h16a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/></svg>' +
      '<span class="lr-dot" aria-hidden="true"></span></button>');
    var teaser = el('<div class="lr-teaser" role="status">👋 Need a quick quote? We usually reply in minutes!</div>');
    var panel = el('<div class="lr-panel" id="lr-panel" role="dialog" aria-label="Chat with Let\'s Roll Garage Doors">' +
      '<div class="lr-panel-head"><strong>Let\'s Roll Garage Doors</strong><span>🟢 We typically reply in minutes</span>' +
      '<button type="button" class="lr-x" aria-label="Close chat">×</button></div>' +
      '<div class="lr-panel-body">' +
      '<div class="lr-msg">Hey! 👋 Thanks for stopping by. Tell us what\'s going on with your garage door and we\'ll get back to you ASAP.</div>' + deals +
      '<form id="lr-chat-form" novalidate>' +
      '<input class="lr-field" name="name" type="text" placeholder="Your name" autocomplete="name" required>' +
      '<input class="lr-field" name="phone" type="tel" placeholder="Phone number" autocomplete="tel" inputmode="tel" required>' +
      '<select class="lr-field" name="service" aria-label="Service needed">' +
      '<option value="">What do you need?</option><option>Broken spring repair</option><option>Door off track</option><option>Opener not working</option><option>New garage door install</option><option>General tune-up</option><option>Other</option></select>' +
      '<textarea class="lr-field" name="details" placeholder="Details (optional)"></textarea>' +
      '<div class="lr-err" role="alert">Please add your name and a phone number.</div>' +
      '<button type="submit" class="lr-btn">Send My Request</button></form></div></div>');
    document.body.appendChild(teaser);
    document.body.appendChild(panel);
    document.body.appendChild(chatBtn);

    var teaserTimer, hideTimer;
    function hideTeaser() { teaser.classList.remove('lr-on'); clearTimeout(hideTimer); }
    function openChat() {
      hideTeaser();
      clearTimeout(teaserTimer);
      panel.classList.add('lr-open');
      chatBtn.setAttribute('aria-expanded', 'true');
      var f = panel.querySelector('input[name=name]');
      if (f && f.offsetParent) f.focus();
    }
    function closeChat() {
      panel.classList.remove('lr-open');
      chatBtn.setAttribute('aria-expanded', 'false');
    }
    chatBtn.addEventListener('click', function () { panel.classList.contains('lr-open') ? closeChat() : openChat(); });
    panel.querySelector('.lr-x').addEventListener('click', closeChat);
    teaser.addEventListener('click', openChat);

    teaserTimer = setTimeout(function () {
      var popOpen = document.getElementById('lr-pop') && !document.getElementById('lr-pop').hidden;
      if (panel.classList.contains('lr-open') || popOpen) return;
      teaser.classList.add('lr-on');
      hideTimer = setTimeout(hideTeaser, TEASER_HIDE);
    }, TEASER_DELAY);

    panel.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target, name = f.name.value.trim(), phone = f.phone.value.trim();
      var err = f.querySelector('.lr-err');
      if (!name || phone.replace(/\D/g, '').length < 7) { err.style.display = 'block'; return; }
      err.style.display = 'none';
      sendLead('chat', { name: name, phone: phone, service: f.service.value, details: f.details.value.trim() });
      var body = panel.querySelector('.lr-panel-body');
      body.innerHTML = '<div class="lr-thanks"><h3>Thanks, ' + name.replace(/[<>&"]/g, '') + '!</h3>' +
        '<p>We got your message and will reach out shortly. Need us right now? Call <a href="' + TEL + '" style="color:var(--orange,#c24c07);font-weight:700">' + PHONE + '</a>.</p>' +
        (DEALS_LIVE ? '<a class="lr-btn" href="coupons.html">View October Deals →</a>' : '<a class="lr-btn" href="' + TEL + '">Call ' + PHONE + '</a>') + '</div>';
    });

    /* ---------- coupon pop-up ---------- */
    if (!DEALS_LIVE || store(true, 'lrPopSeen')) return;
    var pop = el('<div class="lr-pop" id="lr-pop" role="dialog" aria-modal="true" aria-labelledby="lr-pop-title" hidden>' +
      '<div class="lr-pop-card">' +
      '<button type="button" class="lr-x" aria-label="Close">×</button>' +
      '<div class="lr-pop-head"><span class="lr-pop-badge">October Only</span>' +
      '<div class="lr-pop-amt">$30 to $79 OFF</div><div class="lr-pop-sub" id="lr-pop-title">Spring Repair - October Only</div></div>' +
      '<div class="lr-pop-body" id="lr-pop-body">' +
      '<p>Enter your name and phone to unlock your coupon code.</p>' +
      '<form id="lr-pop-form" novalidate>' +
      '<input class="lr-field" name="name" type="text" placeholder="Your name" autocomplete="name" required>' +
      '<input class="lr-field" name="phone" type="tel" placeholder="Phone number" autocomplete="tel" inputmode="tel" required>' +
      '<div class="lr-err" role="alert">Please add your name and a phone number.</div>' +
      '<button type="submit" class="lr-btn">Unlock My October Deals</button>' +
      '<button type="button" class="lr-link" data-dismiss>No thanks, I\'ll pay full price</button></form></div>' +
      '<div class="lr-pop-foot">Ends October 31 - limited availability</div></div></div>');
    document.body.appendChild(pop);

    var lastFocus = null;
    function openPop() {
      if (panel.classList.contains('lr-open')) { setTimeout(openPop, 4000); return; }
      hideTeaser();
      lastFocus = document.activeElement;
      pop.hidden = false;
      document.body.style.overflow = 'hidden';
      requestAnimationFrame(function () { pop.classList.add('lr-show'); });
      var f = pop.querySelector('input[name=name]');
      if (f) f.focus();
      store(false, 'lrPopSeen', '1');
    }
    function closePop() {
      pop.classList.remove('lr-show');
      document.body.style.overflow = '';
      setTimeout(function () { pop.hidden = true; }, 220);
      if (lastFocus && lastFocus.focus) try { lastFocus.focus(); } catch (e) {}
    }
    pop.addEventListener('click', function (e) { if (e.target === pop) closePop(); });
    pop.querySelector('.lr-x').addEventListener('click', closePop);
    pop.querySelector('[data-dismiss]').addEventListener('click', closePop);
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (!pop.hidden) closePop(); else if (panel.classList.contains('lr-open')) closeChat();
    });
    pop.querySelector('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var f = e.target, name = f.name.value.trim(), phone = f.phone.value.trim();
      var err = f.querySelector('.lr-err');
      if (!name || phone.replace(/\D/g, '').length < 7) { err.style.display = 'block'; return; }
      err.style.display = 'none';
      sendLead('coupon-popup', { name: name, phone: phone, code: 'SPRING30' });
      pop.querySelector('#lr-pop-body').innerHTML = '<div class="lr-thanks"><h3>Your coupon is unlocked!</h3>' +
        '<div class="lr-code"><small>Your code</small><strong>SPRING30</strong></div>' +
        '<p>Mention this code when you call for $30 off a single spring repair. Replacing both springs? Use <strong>SPRING79</strong> for $79 off. Cannot be combined with other offers. Expires October 31, 2026.</p>' +
        '<a class="lr-btn" href="' + TEL + '">Call Now &amp; Save</a>' +
        '<a class="lr-link" href="coupons.html">See all October deals</a></div>';
    });
    setTimeout(openPop, POPUP_DELAY);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
