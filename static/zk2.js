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
        content = "["+note_title+"](zk://"+note_id+")";
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
    console.log('show_top_note');
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

// =============
// = Callbacks =
// =============
function update_list(data) {
    console.log('update_list');
    var list_box = document.getElementById("list_box");
    list_box.innerHTML = data;
    show_top_note();
    // show_stats();
}

function update_tag_box(data) {
    document.getElementById("tag_box").innerHTML = data;
}

function update_note(data) {
    var note = JSON.parse(data);
    document.getElementById("note_header").innerHTML = note.header;
    document.getElementById("note_body").innerHTML = note.body;
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
