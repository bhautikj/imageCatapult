$(function() {
$( "#uploadImageList" ).selectable();
});

$(function () {
    $('#fileupload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                var li = $('<li>');
                li.attr('class','ui-widget-content')
                var img = $('<img id="dynamic">');
                img.attr('src', file.displayurl + '.thumb.jpg');
                img.appendTo(li);
                $('#uploadImageList').append(li);
            });
        }
    });
});