var locale = "apac";
var siteVersion = "?v2";
var gameVersion = "?v2";
var content, isPlayingGame;

var jigsawLookUp = {
    "mission01": "crashhopper",
    "mission02": "stinkfly",
    "mission03": "ball_weevil",
    "mission04": "armodrillo",
    "mission05": "humungousaur"
};

function buildSwfHtml(swfUrl, flashvars, width, height, bgcolor, wmode) {
    var fvParts = [];
    for (var k in flashvars) {
        if (Object.prototype.hasOwnProperty.call(flashvars, k)) {
            fvParts.push(k + '=' + flashvars[k]);
        }
    }
    var flashvarsStr = fvParts.join('&');
    var bg = bgcolor || '#FFFFFF';
    var wm = wmode   || 'transparent';

    return ''
        + '<object type="application/x-shockwave-flash"'
        + ' classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"'
        + ' data="' + swfUrl + '"'
        + ' id="ben10_content"'
        + ' width="' + width + '"'
        + ' height="' + height + '"'
        + ' tabindex="0"'
        + ' style="visibility:visible;">'
        +   '<param name="movie" value="' + swfUrl + '">'
        +   '<param name="base" value="">'
        +   '<param name="allowScriptAccess" value="always">'
        +   '<param name="allowscriptaccess" value="always">'
        +   '<param name="bgcolor" value="' + bg + '">'
        +   '<param name="wmode" value="' + wm + '">'
        +   '<param name="menu" value="true">'
        +   '<param name="scale" value="noscale">'
        +   '<param name="allowFullScreen" value="true">'
        +   '<param name="flashvars" value="' + flashvarsStr + '">'
        +   '<embed type="application/x-shockwave-flash"'
        +     ' src="' + swfUrl + '"'
        +     ' name="ben10_content"'
        +     ' width="' + width + '"'
        +     ' height="' + height + '"'
        +     ' allowScriptAccess="always"'
        +     ' allowFullScreen="true"'
        +     ' bgcolor="' + bg + '"'
        +     ' wmode="' + wm + '"'
        +     ' menu="true"'
        +     ' scale="noscale"'
        +     ' flashvars="' + flashvarsStr + '">'
        + '</object>';
}

function embedFlash(swfUrl, flashvars, width, height, bgcolor, wmode) {
    var html = buildSwfHtml(swfUrl, flashvars, width, height, bgcolor, wmode);

    var oldWrap = document.getElementById('content_wrap');
    if (!oldWrap) {
        console.warn('[AU2] embedFlash: no hay #content_wrap');
        return;
    }

    var parent = oldWrap.parentNode;
    var oldClass = oldWrap.className;

    var newWrap = document.createElement('div');
    newWrap.id = 'content_wrap';
    newWrap.className = oldClass;
    newWrap.innerHTML = html;

    parent.replaceChild(newWrap, oldWrap);

    console.log('[AU2] embedFlash ->', swfUrl);
    console.log('[AU2]   flashvars:', flashvars);

    setTimeout(contentFocus, 700);
}

function loadContent(section, initialLoad) {
    $('#back_btn').css({ "display": "none" });
    var flashvars = {
        string_configPath:   "xml/config.xml",
        string_targetSWF:    "launcher.swf" + siteVersion,
        string_locale:       locale,
        string_startSection: section,
        string_preventCache: "false",
        string_initialLoad:  initialLoad
    };
    embedFlash("preloader.swf", flashvars, 944, 600, "#FFFFFF", "transparent");
    isPlayingGame = false;
}

function loadGame(missionID) {
    console.log('[AU2] loadGame() -> missionID =', missionID);

    $('#back_btn').css({ "display": "block" });

    var flashvars = {
        locale:    locale,
        missionID: missionID
    };
    embedFlash("missions.swf" + gameVersion, flashvars, 820, 460, "#000000", "opaque");
    isPlayingGame = true;
}

function init() {
    $('#back_btn').click(navigateToMissions);
    try {
        var m = (location.search.match(/[?&]mission=(mission\d{2})/) || [])[1];
        if (m) {
            console.log('[AU2] Auto-play de misión por URL:', m);
            setTimeout(function() { loadGame(m); }, 800);
        }
    } catch (e) { }
}

window.onload = init;

function playMission(missionID) {
    console.log('[AU2] ExternalInterface: playMission', missionID);
    loadGame(missionID);
}

function navigateToMissions() {
    console.log('[AU2] ExternalInterface: navigateToMissions');
    loadContent("MISSIONSELECT", "false");
}

function navigateToHome() {
    console.log('[AU2] ExternalInterface: navigateToHome');
    loadContent("HOME", "false");
}

function closeWindow() { window.close(); }

function getFlashFocus() { setTimeout(contentFocus, 700); }

function contentFocus() {
    content = document.getElementById("ben10_content");
    if (content) {
        content.tabIndex = 0;
        if (content.focus) content.focus();
    }
}

function showBackground() {
    addClass(document.getElementById("container"), "background_show");
}

function playJigsaw(missionID) {
    $('#jigsaw').css({ "visibility": "visible" });
    $('#jigsaw_btn_close').click(hideJigsaw);

    var jigsawID   = jigsawLookUp[missionID];
    var assetsPath = "assets/jigsaws/" + jigsawID + "/";

    var html = buildSwfHtml(
        'assets/jigsaws/turner_jigsaw.swf',
        { path: assetsPath, debug_mode: "false", region: locale },
        600, 400, '#000000', 'transparent'
    );

    var wrap = document.getElementById('jigsaw');
    if (wrap) wrap.innerHTML = html;
}

function hideJigsaw() {
    $('#jigsaw').css({ "visibility": "hidden" });
    $('#jigsaw_btn_close').unbind('click');
    replaceSwfWithEmptyDiv("jigsaw_flash");
    var c = document.getElementById("ben10_content");
    if (c && c.jigsawClosed) c.jigsawClosed();
}

function replaceSwfWithEmptyDiv(targetID) {
    var el = document.getElementById(targetID);
    if (el && el.parentNode) {
        var div = document.createElement("div");
        div.setAttribute("id", targetID);
        el.parentNode.replaceChild(div, el);
    }
}

function switchContentClass(clazz) {
    var el = document.getElementById("content_wrap");
    if (el) el.className = clazz;
}

function hasClass(ele, cls) {
    return ele && ele.className && ele.className.match(new RegExp('(\\s|^)' + cls + '(\\s|$)'));
}

function addClass(ele, cls) {
    if (ele && !hasClass(ele, cls)) ele.className += " " + cls;
}

function removeClass(ele, cls) {
    if (hasClass(ele, cls)) {
        var reg = new RegExp('(\\s|^)' + cls + '(\\s|$)');
        ele.className = ele.className.replace(reg, '');
    }
}

function replaceClass(ele, oldClass, newClass) {
    if (hasClass(ele, oldClass)) {
        removeClass(ele, oldClass);
        addClass(ele, newClass);
    }
}

function toggleClass(ele, cls1, cls2) {
    if (hasClass(ele, cls1)) replaceClass(ele, cls1, cls2);
    else if (hasClass(ele, cls2)) replaceClass(ele, cls2, cls1);
    else addClass(ele, cls1);
}

window.au2Save = function(jsonString) {
    try {
        var username = localStorage.getItem('au2_username')
                    || sessionStorage.getItem('au2_username');
        if (!username) return 'no-session';
        var payload = JSON.parse(jsonString);
        fetch('/api/save_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, data: payload })
        });
        if (typeof window.au2NotifySave === 'function') window.au2NotifySave();
        return 'ok';
    } catch (e) {
        console.error('[AU2] au2Save error:', e);
        return 'error';
    }
};

window.au2Load = function() {
    return '';
};