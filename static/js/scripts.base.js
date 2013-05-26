function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function(){
    $('form button').on('click', function(){
        var f = $(this).get(0).form;

        if (typeof(f) !== 'undefined') {
            if (this.type && this.type != 'submit')
                return;

            $("input[type='hidden'][name='"+this.name+"']", f).remove();

            if (typeof(this.attributes.value) !== 'undefined')
                $(f).append('<input name="'+this.name+'" value="'+this.attributes.value.value+'" type="hidden">');

            $(f).trigger('submit');
        }
    });
});