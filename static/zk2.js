// ======================
// = API for webpage =
// ======================

function reset() {
    filter_notes('');
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
    var note_title = event.target.innerHTML;
    var note_id = event.target.parentElement.id;
    var content = "zk://"+note_id+" \""+note_title+"\"";
    if (event.altKey) {
        content = "["+note_title.trim()+"](zk://"+note_id+")";
    }
    event.dataTransfer.setData("text", content);
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

function show_zk() {
    var link = this.href.slice(5);
    show_note(link);
}

function mangle_links(element) {
  var links = element.getElementsByTagName('a');
  var re_http = /^https?:\/\//;
  var re_zk = /^zk:\/\/(\d+)/;
  for (var i = 0; i < links.length; i++) {
    var url = links[i].href;
    var zk_match = re_zk.exec(url);
    if (zk_match != null) {
        links[i].addEventListener('click', show_zk, false); 
    } else if (re_http.test(url)) {
        links[i].innerHTML += '<img src="static/if_globe_646196.svg" width="12" height="12" />'
    }
  }
}

function edit(note_id) {
    get_request("edit/"+note_id, function(){});
}

function archive(note_id) {
    get_request("archive/"+note_id, function(){});
}
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
    mangle_links(document.getElementById("note_body"));
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
