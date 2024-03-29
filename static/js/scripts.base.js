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

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(?=\d*\.)(\d{3})+(?!\d))/g, '_');
}

function _showErrorTooltip(selector, text) {
    selector.tooltip({title: text, trigger: 'manual'}).tooltip('show');
}

function _hideErrorTooltip(selector, text) {
    selector.tooltip('destroy');
}

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

$(document).on('show.bs.modal', '.modal', function() {
    $(this).find('.modal-success').remove();
    $(this).find('.modal-error').remove();
});

function _alertModal(type, title, message) {
    var modal = $('#alert-modal');
    modal.find('.modal-header h3').html(title)
    modal.find('.modal-body').html('<p class="' + type + '">' + message + '</p>')
    modal.modal();
}

function _addModalSuccessMessage(modal_id, message) {
    $('#' + modal_id + ' .modal-success').remove();
    $('#' + modal_id + ' .modal-header').after('<div class="modal-success"><i class="icon-ok-sign icon-white"></i> ' + message + '</div>');
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
            delay: 2000,
            history: false,
            icon: false,
            sticker: false,
            text: message,
            title: title,
            type: type
        });
    }
}

function initializeRegistrationModal() {
    var registration_modal = $('#registration-modal');

    registration_modal.find('input').keypress(function(e) {
        if(e.which == 13) {
            $(this).closest('form').submit();
        }
    });

    registration_modal.on('shown', function() {
        registration_modal.find('.email-login .actions .error').remove();
        registration_modal.find('.email-register .actions .error').remove();
    });
/*
    registration_modal.find('.email-login button').on('click', function() {
        var email = registration_modal.find('.email-login input[name="email"]').val();
        var password = registration_modal.find('.email-login input[name="password"]').val();

        if(email && password) {
            registration_modal.find('.email-login button').prop('disabled', true);
            var jqxhr = $.post('/ajax/email/login/', {email:email, password:password}, function(response) {
                if(response.status == 'success') {
                    window.location.reload();
                } else {
                    registration_modal.find('.email-login button').prop('disabled', false);
                    registration_modal.find('.email-login .actions .error').remove();
                    registration_modal.find('.email-login .actions').prepend('<div class="error">Login failed. ' + response.message + '</div>');
                }
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                registration_modal.find('.email-login button').prop('disabled', false);
                registration_modal.find('.email-login .actions .error').remove();
                registration_modal.find('.email-login .actions').prepend('<div class="error">Login failed. ' + errorThrown + '</div>');
            });
        }

        return false;
    });

    registration_modal.find('.email-register button').on('click', function() {
        var email = registration_modal.find('.email-register input[name="email"]').val();

        if(email) {
            registration_modal.find('.email-register button').prop('disabled', true);
            var jqxhr = $.post('/ajax/email/register/', {email:email}, function(response) {
                registration_modal.find('.email-register button').prop('disabled', false);
                if(response.status == 'success') {
                    registration_modal.modal('hide');
                    _alertModal('success', 'Register successful', 'Please confirm your email address from an email we sent to you.');
                } else {
                    registration_modal.find('.email-register .actions .error').remove();
                    registration_modal.find('.email-register .actions').prepend('<div class="error">Register failed. ' + response.message + '</div>');
                }
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                registration_modal.find('.email-register button').prop('disabled', false);
                registration_modal.find('.email-register .actions .error').remove();
                registration_modal.find('.email-register .actions').prepend('<div class="error">Register failed. ' + errorThrown + '</div>');
            });
        }

        return false;
    });*/
}

moment.lang('th', {
    months : "มกราคม_กุมภาพันธ์_มีนาคม_เมษายน_พฤษภาคม_มิถุนายน_กรกฎาคม_สิงหาคม_กันยายน_ตุลาคม_พฤศจิกายน_ธันวาคม".split("_"),
    monthsShort : "มกรา_กุมภา_มีนา_เมษา_พฤษภา_มิถุนา_กรกฎา_สิงหา_กันยา_ตุลา_พฤศจิกา_ธันวา".split("_"),
    weekdays : "อาทิตย์_จันทร์_อังคาร_พุธ_พฤหัสบดี_ศุกร์_เสาร์".split("_"),
    weekdaysShort : "อาทิตย์_จันทร์_อังคาร_พุธ_พฤหัส_ศุกร์_เสาร์".split("_"), // yes, three characters difference
    weekdaysMin : "อา._จ._อ._พ._พฤ._ศ._ส.".split("_"),
    longDateFormat : {
        LT : "H นาฬิกา m นาที",
        L : "YYYY/MM/DD",
        LL : "D MMMM YYYY",
        LLL : "D MMMM YYYY เวลา LT",
        LLLL : "วันddddที่ D MMMM YYYY เวลา LT"
    },
    meridiem : function (hour, minute, isLower) {
        if (hour < 12) {
            return "ก่อนเที่ยง";
        } else {
            return "หลังเที่ยง";
        }
    },
    calendar : {
        sameDay : '[วันนี้ เวลา] LT',
        nextDay : '[พรุ่งนี้ เวลา] LT',
        nextWeek : 'dddd[หน้า เวลา] LT',
        lastDay : '[เมื่อวานนี้ เวลา] LT',
        lastWeek : '[วัน]dddd[ที่แล้ว เวลา] LT',
        sameElse : 'L'
    },
    relativeTime : {
        future : "อีก %s",
        past : "%sที่แล้ว",
        s : "ไม่กี่วินาที",
        m : "1 นาที",
        mm : "%d นาที",
        h : "1 ชั่วโมง",
        hh : "%d ชั่วโมง",
        d : "1 วัน",
        dd : "%d วัน",
        M : "1 เดือน",
        MM : "%d เดือน",
        y : "1 ปี",
        yy : "%d ปี"
    }
});