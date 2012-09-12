/* Dust filters */

var evenodd = 0;
dust.filters.evenodd = function(body) {
    /* This filter uses a global var to toggle alternating "even"/"odd" values.
     * It ignores it's argument. The use as a global allows using it in a
     * nested context (for example a tree), without keeping track of parity of
     * parent entries
     */
    evenodd += 1;
    if (evenodd % 2 == 0)
        return "even"
    else
        return "odd";
}

/* Foldable tree UI */
function toggleCollapsed() {
    /* Toggles collapsed/uncollapsed CSS class on the parent of $(this) */
    var listItem = $(this).parent();
    listItem.children("ul").slideToggle();
    if (listItem.hasClass("uncollapsed")) {
        listItem.removeClass("uncollapsed");
        listItem.addClass("collapsed");
    } else if (listItem.hasClass("collapsed")) {
        listItem.removeClass("collapsed");
        listItem.addClass("uncollapsed");
    }
}

/* Template parsing and context UI */

function showContext(data) {
    /* Called when receiving template context var details from AJAX call */
    /* Renders and displays the context editor UI */
    if (data.error) {
        /* data.error contains the html representation of form.errors */
        $("#context-tree").html(data.error);
    } else {
        /* Render dust template */
        var tree = {"children": data};
        var result = "";
        dust.render("context", tree, function(err, out) { result += out}); 
        $("#context-tree").html(result);
        /* Enable tree collapsing */
        $(function () {
            $("li > label").click(toggleCollapsed);
        });
        /* Once we get the context, hide the button, show the preview one */
        $("#get-context").hide();
        $("#preview-submit").show();
    }
}
function getContext() {
    /* Send template name to ajax call to get context and render the UI
     * (see showContext() for details)
     */
    var templateName = $("#id_template").val();
    $.getJSON(
        parse_url,
        {template: templateName},
        showContext
    );
    return false;
}

function buildContext(elem, data) {
    /* Gather the data from the context editor UI into a properly formed JSON.
     * elem is a <ul> element, and data is a dict. Note that this builds the
     * object recursively
     */
    var children = elem.children("li");
    var i;
    for (i = 0; i < children.length; i++) {
        var input = $(children[i]).find("input");
        /* _str is the string representation, even if it is an object with
         * children
         */
        var node = {"_str": input.val()};
        data[input.attr('name')] = node;
        var subnodes = $(children[i]).children("ul");
        if (subnodes) {
            buildContext(subnodes, node);
        }
    }
}

function sendContext() {
    /* JSONify user defined context */
    var data = {};
    /* DOM -> object */
    buildContext($("#context-tree > ul"), data);
    /* Object -> JSON stored in a hidden input */
    $("#id_context").val($.toJSON(data));
    /* Proceed with form submit */
    return true;
}

$(function () {
    /* Bind UI elements */
    $("#get-context").click(getContext);
    $("#preview-submit").click(sendContext);
    var togglePreview = function () {$("#preview-ui").fadeToggle();};
    $("#hide-preview").click(togglePreview);
    $("#show-preview").click(togglePreview);

    /* If the template name is updated, the list of context vars must be
     * updated too. So show only the update button but not the preview button
     */
    $("#preview-submit").hide();
    $("#id_template").change(function () {
        $("#get-context").show();
        $("#preview-submit").hide();
    })
});

