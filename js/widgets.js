/* Let's Roll Garage Doors: coupon pop-up + floating chat widget.
   Loaded with defer on every page. Styles are injected here so no extra CSS request blocks rendering. */
(function () {
  'use strict';

  var TEL = 'tel:+15129474451';
  var PHONE = '(512) 947-4451';
  var ACCESS_KEY = '04548151-caf0-4166-b696-19dafbd20e6e'; // same Web3Forms key as the quote form
  var SEND_TO_EMAIL = true; // set to false to only console.log leads
  var DEALS_END = new Date('2026-11-12T00:00:00-06:00').getTime(); // deals run through Nov 11, 2026
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

  var css = ".lr-pop{position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(16,33,61,.8);opacity:0;transition:opacity .25s ease}.lr-pop[hidden]{display:none}.lr-pop.lr-show{opacity:1}.lr-pop-card{position:relative;width:100%;max-width:410px;max-height:calc(100vh - 32px);overflow:auto;background:#f7f4ec;border:3px solid #10213d;border-radius:0;box-shadow:10px 10px 0 #6cc4f0;font-family:Archivo,system-ui,sans-serif;color:#10213d;transform:translateY(16px) rotate(-1.4deg);transition:transform .45s cubic-bezier(.16,1,.3,1)}.lr-show .lr-pop-card{transform:rotate(-.6deg)}.lr-pop-head{position:relative;background:#10213d;color:#f7f4ec;text-align:left;padding:38px 24px 22px}.lr-pop-head::before{content:\"\";position:absolute;left:0;right:0;top:0;height:14px;background:repeating-linear-gradient(135deg,#6cc4f0 0 16px,#10213d 16px 32px)}.lr-pop-badge{display:inline-block;background:#6cc4f0;color:#10213d;font:500 11px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;padding:5px 10px;border-radius:0;margin-bottom:12px}.lr-pop-amt{font-family:\"Archivo Black\",Archivo,sans-serif;font-size:42px;line-height:.98;letter-spacing:-.02em;text-transform:uppercase;color:#6cc4f0}.lr-pop-sub{font:500 12px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;margin-top:10px;opacity:.9}.lr-x{position:absolute;top:22px;right:10px;width:38px;height:38px;border:2px solid #f7f4ec;border-radius:0;background:transparent;color:#f7f4ec;font-size:22px;line-height:1;cursor:pointer;z-index:2}.lr-x:hover{background:#6cc4f0;color:#10213d;border-color:#6cc4f0}.lr-pop-body{padding:22px 24px 8px}.lr-pop-body p{margin:0 0 14px;font-size:15px;line-height:1.5;color:#2c3a55}.lr-field{display:block;width:100%;box-sizing:border-box;margin:0 0 12px;padding:12px 14px;min-height:46px;font:inherit;font-size:16px;border:2px solid #10213d;border-radius:0;background:#fff;color:#10213d}.lr-field:focus{outline:3px solid #6cc4f0;outline-offset:0}textarea.lr-field{resize:vertical;min-height:70px}.lr-btn{display:block;width:100%;box-sizing:border-box;text-align:center;text-decoration:none;border:3px solid #10213d;border-radius:0;background:#6cc4f0;color:#10213d;font-family:\"Archivo Black\",Archivo,sans-serif;font-size:16px;text-transform:uppercase;letter-spacing:.02em;padding:13px 18px;min-height:50px;cursor:pointer;box-shadow:5px 5px 0 #10213d;transition:transform .35s cubic-bezier(.16,1,.3,1),box-shadow .35s cubic-bezier(.16,1,.3,1)}.lr-btn:hover{transform:translate(-2px,-2px);box-shadow:8px 8px 0 #10213d}.lr-btn:active{transform:translate(3px,3px);box-shadow:2px 2px 0 #10213d}.lr-btn[disabled]{opacity:.6;cursor:default}.lr-link{display:block;width:100%;margin:14px 0 4px;min-height:36px;border:0;background:none;color:#10213d;font:500 12px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;text-decoration:underline;text-decoration-color:#6cc4f0;text-decoration-thickness:3px;text-underline-offset:4px;cursor:pointer;text-align:center}.lr-pop-foot{background:#e8dcc0;color:#10213d;text-align:center;font:500 11px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;padding:12px 14px;margin-top:12px;border-top:3px dashed #10213d}.lr-code{border:3px dashed #10213d;background:#fff;text-align:center;padding:12px;margin:4px 0 16px}.lr-code small{display:block;font:500 11px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.12em;text-transform:uppercase;color:#5b6475}.lr-code strong{font-family:\"Archivo Black\",Archivo,sans-serif;font-size:28px;letter-spacing:.1em;color:#10213d}.lr-err{color:#10213d;background:#6cc4f0;font-size:13px;font-weight:600;padding:6px 10px;margin:-4px 0 10px;display:none}.lr-chat-btn{position:fixed;right:16px;bottom:90px;z-index:9998;width:60px;height:60px;border:3px solid #10213d;border-radius:0;background:#6cc4f0;color:#10213d;cursor:pointer;box-shadow:5px 5px 0 #10213d;display:flex;align-items:center;justify-content:center;transition:transform .35s cubic-bezier(.16,1,.3,1),box-shadow .35s cubic-bezier(.16,1,.3,1)}.lr-chat-btn:hover{transform:translate(-2px,-2px);box-shadow:8px 8px 0 #10213d}.lr-chat-btn svg{width:28px;height:28px;fill:#10213d}.lr-dot{position:absolute;top:-8px;right:-8px;width:15px;height:15px;border-radius:50%;background:#22c55e;border:3px solid #10213d;animation:lrPulse 1.8s infinite}@keyframes lrPulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.6)}70%{box-shadow:0 0 0 9px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}.lr-teaser{position:fixed;right:16px;bottom:164px;z-index:9998;max-width:240px;background:#fff;color:#10213d;font:600 14px/1.4 Archivo,system-ui,sans-serif;padding:12px 14px;border:3px solid #10213d;border-radius:0;box-shadow:5px 5px 0 #10213d;display:none;cursor:pointer}.lr-teaser.lr-on{display:block;animation:lrIn .3s ease}@keyframes lrIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}.lr-panel{position:fixed;right:16px;bottom:164px;z-index:9999;width:360px;max-width:calc(100vw - 24px);max-height:calc(100vh - 184px);display:none;flex-direction:column;background:#f7f4ec;border:3px solid #10213d;border-radius:0;box-shadow:8px 8px 0 #10213d;overflow:hidden;font-family:Archivo,system-ui,sans-serif;color:#10213d}.lr-panel.lr-open{display:flex}.lr-panel-head{background:#10213d;color:#f7f4ec;padding:18px 18px 14px;position:relative}.lr-panel-head::before{content:\"\";position:absolute;left:0;right:0;top:0;height:8px;background:repeating-linear-gradient(135deg,#6cc4f0 0 12px,#10213d 12px 24px)}.lr-panel-head strong{display:block;font-family:\"Archivo Black\",Archivo,sans-serif;font-weight:400;font-size:18px;text-transform:uppercase;letter-spacing:-.01em}.lr-panel-head span{font:500 11px \"IBM Plex Mono\",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;opacity:.9}.lr-panel-head .lr-x{top:12px;right:12px;width:34px;height:34px}.lr-panel-body{padding:16px 16px 14px;overflow:auto;background:#e8dcc0}.lr-msg{background:#fff;border:2px solid #10213d;border-radius:0;padding:11px 13px;margin:0 0 10px;font-size:14.5px;line-height:1.5;max-width:92%}.lr-msg a{color:#10213d;font-weight:700;text-decoration:underline;text-decoration-color:#6cc4f0;text-decoration-thickness:3px}.lr-panel form{margin-top:14px}.lr-thanks{text-align:center;padding:10px 4px}.lr-thanks h3{font-family:\"Archivo Black\",Archivo,sans-serif;font-weight:400;text-transform:uppercase;font-size:21px;margin:0 0 8px}.lr-thanks p{font-size:14.5px;color:#2c3a55;margin:0 0 14px}@media(max-width:480px){.lr-panel{right:8px;left:8px;width:auto;max-width:none;bottom:150px;max-height:calc(100vh - 170px)}.lr-teaser{right:12px}.lr-chat-btn{right:12px}.lr-pop-amt{font-size:36px}}@media(prefers-reduced-motion:reduce){.lr-dot{animation:none}.lr-pop,.lr-pop-card,.lr-btn,.lr-chat-btn{transition:none}}";

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
      ? '<div class="lr-msg">🎟️ Ask about our current specials: up to $79 off spring repairs!</div>'
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
        (DEALS_LIVE ? '<a class="lr-btn" href="coupons.html">View Current Deals →</a>' : '<a class="lr-btn" href="' + TEL + '">Call ' + PHONE + '</a>') + '</div>';
    });

    /* ---------- coupon pop-up ---------- */
    if (!DEALS_LIVE || store(true, 'lrPopSeen')) return;
    var pop = el('<div class="lr-pop" id="lr-pop" role="dialog" aria-modal="true" aria-labelledby="lr-pop-title" hidden>' +
      '<div class="lr-pop-card">' +
      '<button type="button" class="lr-x" aria-label="Close">×</button>' +
      '<div class="lr-pop-head"><span class="lr-pop-badge">Limited Time</span>' +
      '<div class="lr-pop-amt">$30 to $79 OFF</div><div class="lr-pop-sub" id="lr-pop-title">Spring Repair Specials</div></div>' +
      '<div class="lr-pop-body" id="lr-pop-body">' +
      '<p>Enter your name and phone to unlock your coupon code.</p>' +
      '<form id="lr-pop-form" novalidate>' +
      '<input class="lr-field" name="name" type="text" placeholder="Your name" autocomplete="name" required>' +
      '<input class="lr-field" name="phone" type="tel" placeholder="Phone number" autocomplete="tel" inputmode="tel" required>' +
      '<div class="lr-err" role="alert">Please add your name and a phone number.</div>' +
      '<button type="submit" class="lr-btn">Unlock My Deals</button>' +
      '<button type="button" class="lr-link" data-dismiss>No thanks, I\'ll pay full price</button></form></div>' +
      '<div class="lr-pop-foot">Ends November 11 - limited availability</div></div></div>');
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
        '<p>Mention this code when you call for $30 off a single spring repair. Replacing both springs? Use <strong>SPRING79</strong> for $79 off. Cannot be combined with other offers. Expires November 11, 2026.</p>' +
        '<a class="lr-btn" href="' + TEL + '">Call Now &amp; Save</a>' +
        '<a class="lr-link" href="coupons.html">See all current deals</a></div>';
    });
    setTimeout(openPop, POPUP_DELAY);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
