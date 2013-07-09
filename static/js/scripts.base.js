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

$('.modal').on('show', function() {
    $(this).find('.modal-error').remove();
});

function _alertModal(type, title, message) {
    var modal = $('#alert-modal');
    modal.find('.modal-header h3').html(title)
    modal.find('.modal-body').html('<p class="' + type + '">' + message + '</p>')
    modal.modal();
}

function _addModalErrorMessage(modal_id, message) {
    $('#' + modal_id + ' .modal-error').remove();
    $('#' + modal_id + ' .modal-header').after('<div class="modal-error"><i class="icon-exclamation-sign icon-white"></i> ' + message + '</div>');
}

function _notify(type, title, message) {
    if(type == 'error') {
        $.pnotify({
            addclass: 'custom',
            animation: 'none',
            hide: false,
            history: false,
            icon: false,
            sticker: false,
            text: message,
            title: title,
            type: 'error'
        });
    } else {
        $.pnotify({
            addclass: 'custom',
            animation: 'none',
            history: false,
            icon: false,
            sticker: false,
            text: message,
            title: title,
            type: type
        });
    }
}
