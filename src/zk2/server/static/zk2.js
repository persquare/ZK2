// ======================
// = API for webpage =
// ======================

function reset() {
    filter();
    set_tags();
    add_tag_listener(document.getElementById('tag_box'), filter_by_tag);
    add_tag_listener(document.getElementById('list_box'), filter_by_tag);
    document.getElementById('search').focus();
}

function filter() {
    var searchbox = document.getElementById('search');
    var expr = searchbox.value;
    filter_notes(expr);
}

function drag(event) {
    var anfang = event.target.getElementsByClassName("anfang")[0]
    var note_title = anfang.innerHTML.trim();
    var note_id = event.target.id;
    var content = "["+note_title+"](zk://"+note_id+")";
    if (event.altKey) {
        // FIXME: Make this a reflink and put ref on pasteboard
        content = "[FIXME]: zk://"+note_id+" \""+note_title+"\"";
    }
    event.dataTransfer.setData("text/plain", content);
}

// ======================
// = Core functionality =
// ======================
function filter_notes(expr) {
    get_request("query/"+expr+options(), update_list);
}

function options() {
    var sort_key = document.querySelector('input[name="sort_option"]:checked').value
    var reversed = document.querySelector('input[name="reversed_option"]').checked;
    return "?key="+sort_key+"&reversed="+reversed
}

function set_tags() {
    get_request("tags", update_tag_box)
}

function show_top_note() {
    var list_box = document.getElementById("list_box");
    var first = list_box.children[0];
    if (first !== undefined) {
        show_note(first.id);
    }
}

// Primitive
function show_note(note_id) {
    get_request("note/"+note_id, update_note);
    highlight_item(note_id);
}

function highlight_item(note_id) {
    var list_box = document.getElementById('list_box');
    for (var item of list_box.children) {
        if (note_id == item.id) {
          item.style.backgroundColor = '#dfebfe';
        } else {
          item.style.backgroundColor = 'inherit';
        }
    }
}

function show_zk(event) {
    event.preventDefault();
    event.stopPropagation();
    var link = this.href.slice(5);
    show_note(link);
}

function insertAfter(referenceNode, newNode) {
  referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function createPeek(url) {
    var a = document.createElement('a'); 
    a.href = url;
    a.addEventListener('mouseover', peekOn);
    a.addEventListener('mouseout', peekOff);
    a.innerHTML = '<img src="static/if_eye_370084.svg" width="12" height="12" /><iframe class="peek"></iframe>';
    return a
}
    

function mangle_links(element) {
  var preview = [];    
  var links = element.getElementsByTagName('a');
  var re_http = /^https?:\/\//;
  var re_zk = /^zk:\/\/(\d+)/;
  for (var i = 0; i < links.length; i++) {
    var url = links[i].href;
    var zk_match = re_zk.exec(url);
    if (zk_match != null) {
        links[i].addEventListener('click', show_zk, false);
        preview.push(links[i]);
    } else if (re_http.test(url)) {
        // links[i].innerHTML += '<img src="static/if_globe_646196.svg" width="12" height="12" />'
    }
  }
  return preview
}

function edit(note_id) {
    get_request("edit/"+note_id, function(){});
}

function archive(note_id) {
    get_request("archive/"+note_id, function(){});
}

function new_note() {
    get_request("new", function(){});
}


// ================
// = Peek preview =
// ================

function peekOn(evt) {
    let iframe = this.querySelector('.peek');
    let re_zk = /^zk:\/\/(\d+)/;
    var peek_url = this.href;
    var zk_match = re_zk.exec(peek_url);
    if (zk_match != null) {
        peek_url = "peek/" + peek_url.slice(5);
    }
    if (iframe) {
        iframe.src = peek_url;
        iframe.style.display = 'block';
    }
};

function peekOff(evt) {
    let iframe = this.querySelector('.peek');
    if (iframe) {
        iframe.style.display = 'none';
    }
};

// =============
// = Callbacks =
// =============
function update_list(data) {
    var list_box = document.getElementById("list_box");
    list_box.innerHTML = data;
    show_top_note();
    // show_stats();
}

function update_tag_box(data) {
    document.getElementById("tag_box").innerHTML = data;
}

function update_note(note) {
    document.getElementById("preview_pane").innerHTML = note;
    preview = mangle_links(document.getElementById("note_body"));
    for (var i = 0; i < preview.length; i++) {
        insertAfter(preview[i], createPeek(preview[i].href));
    }
}

function filter_by_tag(tag) {
    document.getElementById("search").value = tag;
    filter_notes(tag);
};

// ====================
// = Helper functions =
// ====================

function get_request(url, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callback(this.responseText);
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function add_tag_listener(element, handler) {
    element.addEventListener('click', function(event) {
          if(/\btag\b/.test(event.target.className)) {
              event.preventDefault();
              event.stopPropagation();
              handler(event.target.innerText);
          }
    }, true /* capture */);
}
