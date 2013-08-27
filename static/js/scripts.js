
/*
$(document).ready(function() {
    $('.modal').on('shown', function(){
        $('body').css('overflow', 'hidden');
    }).on('hidden', function(){
        $('body').css('overflow', 'auto');
    });
});*/

function initWorkshopModifyPage(workshop_uid, enable_autosave, page_type) {
    var form_title = $('#id_title');
    var form_activity = $('#control_activity_list');
    var form_story = $('#id_story');
    var form_pictures = $('#upload-pictures');
    var form_pictures_ordering = $('#id_pictures_ordering');
    var form_price = $('#id_price');
    var form_duration = $('#id_duration');
    var form_capacity = $('#id_capacity');
    var form_topic = $('#id_topic');
    var form_place = $('#id_place');

    var _is_saving = false;
    var _is_very_dirty = false;
    var _is_dirty = false;
    var autosave_timer = null;

    // BINDING FORM ACTIONS
    $('.form-footer .button-draft').on('click', function() {
        if($(this).hasClass('disabled')) return false;

        _is_dirty = true;
        _is_very_dirty = true;
        save_changes('draft', true);
        return false;
    });

    $('.form-footer .button-submit-approval').on('click', function() {
        if($(this).hasClass('disabled')) return false;

        _is_dirty = true;
        _is_very_dirty = true;

        $('.form-content').one('saved', function(e, response) {
            window.onbeforeunload = function() {};
            $('#modal-workshop-submitted').modal();
        });

        save_changes('approval', false);
        return false;
    });

    $('.form-footer .button-save-changes').on('click', function() {
        if($(this).hasClass('disabled')) return false;

        _is_dirty = true;
        _is_very_dirty = true;
        save_changes('update', true);
        return false;
    });

    // Initialize Workshop Activities
    function _init_workshop_activities() {
        function _add_new_activity() {
            var new_activity = $('<li class="activity"><i class="icon-remove"></i><i class="icon-reorder"></i><input type="text"/></li>');
            _set_activity_events(new_activity);
            new_activity.insertBefore($('#control_add_activity').parent());
            new_activity.find('input').focus();
        }

        $('#control_add_activity').on('click', function() {
            _add_new_activity();
            return false;
        });

        function _set_activity_events(activity_object) {
            activity_object.find('.icon-remove').popover({
                html: true,
                placement: 'left',
                content: '<a href="#" class="btn btn-mini btn-danger button-activity-remove">Confirm delete</a> <a href="#" class="btn btn-mini button-activity-remove-cancel">Cancel</a>'
            });

            activity_object.find('input').on('change', function() {
                _set_activity_dirty();
            });

            activity_object.find('input').keypress(function(e) {
                if(e.which == 13) {
                    var next_activity = $(this).closest('.activity').next('.activity');

                    if(next_activity.length) {
                        next_activity.find('input').focus();
                    } else {
                        _add_new_activity();
                    }
                }
            });
        }

        function _set_activity_dirty() {
            form_activity.data('dirty', true);
            set_dirty();
        }

        form_activity.sortable({
            distance: 15,
            handle: '.icon-reorder',
            items: 'li.activity',
            placeholder: 'ui-state-highlight',
            tolerance: 'pointer',
            stop: function( event, ui ) {
                _set_activity_dirty();
            }
        });

        $(document).on('click', '.popover .button-activity-remove', function() {
            var activityObject = $(this).closest('.activity');
            activityObject.remove();
            _set_activity_dirty();
            return false;
        });

        $(document).on('click', '.popover .button-activity-remove-cancel', function() {
            $(this).closest('.activity').find('.icon-remove').popover('hide');
            return false;
        });

        _set_activity_events($('#control_activity_list'));
    }

    // Initialize Pictures
    function _init_pictures() {
        var upload_pictures = $('#upload-pictures');
        var upload_pictures_ordering = $('#id_pictures_ordering');
        $('#id_pictures').fileupload({
            dataType: 'json',
            url: '/ajax/workshop/picture/upload/',
            sequentialUploads: true,
            formData: function (form) {return [{name:'uid', value:workshop_uid}, {name:'csrfmiddlewaretoken', value: csrftoken}, {name:'ordering', value: upload_pictures_ordering.val()}];},
            add: function (e, data) {
                $('.form-footer button').addClass('disabled');

                var file = data.files[0];
                var errorObject = null;

                if(typeof file.type != 'undefined' && file.type.indexOf('image/') != 0) {
                    errorObject = $('<li class="error"><div class="dismiss"><a href="#"><i class="icon-remove"></i></a></div><div class="error-text"><i class="icon-warning-sign"></i> ไม่ใช่ไฟล์รูปภาพ</div></li>');
                } else if(file.size > 5000000) {
                    errorObject = $('<li class="error"><div class="dismiss"><a href="#"><i class="icon-remove"></i></a></div><div class="error-text"><i class="icon-warning-sign"></i> ขนาดไฟล์ใหญ่เกิน 5 เมกะไบต์</div></li>');
                }

                if(errorObject) {
                    upload_pictures.append(errorObject);
                    return;
                }

                var uploadingObject = $('<li class="uploading"><div class="progress"><div class="progress-bar" role="progressbar"></div></div><div class="progress-text"><em>0</em>% Complete</div></li>');
                upload_pictures.append(uploadingObject);

                uploadingObject.data('data', data);
                data.context = uploadingObject;

                data.submit();
            },
            progress: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                data.context.find('.progress-bar').attr('aria-valuetransitiongoal', progress).progressbar();
                data.context.find('.progress-text em').text(progress);
            },
            done: function (e, data) {
                data.context.find('.progress-bar').attr('aria-valuetransitiongoal', 100).progressbar();
                data.context.find('.progress-text em').text(100);

                var file = data.files[0];
                var response = data.result;

                if(response.status == 'success') {
                    upload_pictures_ordering.val(response.data.ordering);

                    data.context.removeClass('uploading').addClass('picture');
                    data.context.html('<img src="' + response.data.picture_url + '"><a title="ลบรูปภาพ" class="delete" href="#"><i class="icon-remove icon-white"></i></a>');
                    data.context.attr('picture-uid', response.data.picture_uid);

                } else if(response.status == 'error') {
                    data.context.removeClass('uploading').addClass('error');

                    if(response.message) {
                        data.context.html('<div class="dismiss"><a href="#"><i class="icon-remove"></i></a></div><div class="error-text"><i class="icon-warning-sign"></i> ' + response.message + '</div>');
                    } else {
                        data.context.html('<div class="dismiss"><a href="#"><i class="icon-remove"></i></a></div><div class="error-text"><i class="icon-warning-sign"></i> ไม่สามารถอัพโหลดไฟล์ได้</div>');
                    }
                }

                _reset_form_header();
            },
            fail: function (e, data) {
                if (data.errorThrown == 'abort') {
                    data.context.remove();
                } else {
                    data.context.removeClass('uploading').addClass('error');
                    data.context.html('<div class="dismiss"><a href="#"><i class="icon-remove"></i></a></div><div class="error-text"><i class="icon-warning-sign"></i> ไม่สามารถอัพโหลดไฟล์ได้</div>');
                }
                _reset_form_header();
            }
        });

        upload_pictures.sortable({
            distance: 15,
            handle: 'img',
            items: 'li.picture',
            tolerance: 'pointer',
            placeholder: 'ui-state-highlight',
            stop: function(event, ui) {
                var new_ordering = '';
                upload_pictures.find('li.picture').each(function() {
                    new_ordering = new_ordering + $(this).attr('picture-uid') + ',';
                });
                upload_pictures_ordering.val(new_ordering);

                upload_pictures_ordering.data('dirty', true);
                set_dirty();
            }
        });

        $(document).on('click', '#upload-pictures li.picture a.delete', function() {
            $(this).hide();
            $(this).closest('.picture').prepend('<div class="confirm-delete"><div class="actions"><a href="#" class="style-outline-danger-button button-remove-picture">ลบรูปภาพ</a><a href="#" class="style-outline-button button-remove-picture-cancel">ยกเลิก</a></div></div>');
            return false;
        });

        $(document).on('click', '#upload-pictures .button-remove-picture', function() {
            $('.form-footer button').addClass('disabled');

            if($(this).hasClass('disabled')) {
                return false;
            }

            var picture = $(this).closest('li.picture');
            var delete_actions = picture.find('confirm-delete a');
            delete_actions.addClass('disabled');

            var picture_uid = $(this).closest('li.picture').attr('picture-uid');

            var jqxhr = $.post('/ajax/workshop/picture/delete/', {uid: workshop_uid, picture_uid: picture_uid}, function(response) {
                if(response.status == 'success') {
                    upload_pictures_ordering.val(response.data.ordering);
                    upload_pictures.find('li[picture-uid=' + picture_uid + ']').fadeOut(function() {
                        $(this).remove();
                    });
                } else {
                    delete_actions.removeClass('disabled');
                    picture.find('.confirm-delete').remove();
                    picture.find('.delete').show();

                    if(response.message) {
                        _alertModal('error', 'ไม่สามารถลบรูปได้', response.message);
                    } else {
                        _alertModal('error', 'ไม่สามารถลบรูปได้', 'Unknown error');
                    }
                }

                _reset_form_header();
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                delete_actions.removeClass('disabled');
                picture.find('.confirm-delete').remove();
                picture.find('.delete').show();
                _alertModal('error', 'ไม่สามารถลบรูปได้', 'Unexpected error occurred: ' + errorThrown);
            });

            return false;
        });

        $(document).on('click', '.button-remove-picture-cancel', function() {
            if($(this).hasClass('disabled')) {
                return false;
            }

            var picture = $(this).closest('li.picture');
            picture.find('.confirm-delete').remove();
            picture.find('.delete').show();
            return false;
        });

        $(document).on('click', '#upload-pictures li.error .dismiss a', function() {
            $(this).closest('li.error').remove();
            return false;
        });
    }

    // Initialize Place
    function _init_place() {
        var place_form = $('.place-form');
        var id_place_userdefined = $('#id_place_userdefined');

        $('.button-new-location:not(.disabled)').on('click', function() {
            form_place.find('input[value="userdefined-place"]').trigger('click');

            id_place_userdefined.find('option:first').prop('selected', true);
            place_form.show();
            place_form.find('.head').text('สถานที่ใหม่');

            $('#id_place_id').val('new');
            $('#id_place_name').val('').focus().select();
            $('#id_place_address').val('');
            $('#id_place_province').find('option:first').prop('selected', true);
            $('#id_place_direction').val('');
            $('#id_place_location').val('');

            place_form.find('.minimap').html('').hide();

            return false;
        });

        id_place_userdefined.on('change', function() {
            var selected = id_place_userdefined.find('option:selected').val();

            if(selected) {
                place_form.hide();

                var place_form_loading = $('.place-form-loading');
                place_form_loading.show();

                var jqxhr = $.get('/ajax/workshop/place/get/', {place_id:selected}, function(response) {
                    place_form_loading.hide();
                    if(response.status == 'success') {
                        $('#id_place_id').val(response.data.id);
                        $('#id_place_name').val(response.data.name);
                        $('#id_place_address').val(response.data.address);
                        $('#id_place_province').find('option[value="' + response.data.province_code + '"]').prop('selected', true);
                        $('#id_place_direction').val(response.data.direction);
                        $('#id_place_location').val(response.data.latlng);

                        if(response.data.latlng) {
                            place_form.find('.minimap').html('<img src="http://maps.googleapis.com/maps/api/staticmap?center=' + response.data.latlng + '&zoom=13&size=270x180&markers=color:red%7Clabel:S%7C' + response.data.latlng + '&sensor=false" />').removeClass('hide');
                        } else {
                            place_form.find('.minimap').html('').addClass('hide');
                        }

                        place_form.find('.head').text('แก้ไขสถานที่');
                        place_form.show();

                        form_place.find('input[value="userdefined-place"]').trigger('click');
                        form_place.data('dirty', true);
                        set_dirty();

                    } else {
                        if(response.message) {
                            _notify('error', 'Cannot load', response.message);
                        } else {
                            _notify('error', 'Cannot load', 'Unknown error occurred');
                        }
                    }
                }, 'json');

                jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                    place_form_loading.hide();
                    _notify('error', 'Cannot load', errorThrown);
                });
            } else {
                $('#id_place_id').val('');
                $('#id_place_name').val('');
                $('#id_place_address').val('');
                $('#id_place_province').find('option:first').prop('selected', true);
                $('#id_place_direction').val('');
                $('#id_place_location').val('');

                form_place.find('input[value="userdefined-place"]').trigger('click');
                place_form.hide();
                form_place.data('dirty', true);
                set_dirty();
            }
        });

        var placeModal = $('#modal-place-map');
        var map;
        var marker;
        var geocoder;

        placeModal.on('shown', function() {
            if(!map) {
                var latlng = $('#id_place_location').val();
                var lat, lng;
                var zoom = 8;

                if(latlng) {
                    var latlng_tuple = latlng.split(',');
                    lat = latlng_tuple[0];
                    lng = latlng_tuple[1];
                    zoom = 16;
                } else {
                    lat = 13.727896;
                    lng = 100.524124;
                }

                geocoder = new google.maps.Geocoder();

                var mapOptions = {
                    streetViewControl: false,
                    center: new google.maps.LatLng(lat,lng),
                    zoom: zoom,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };
                map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

                marker = new google.maps.Marker({
                    draggable: true,
                    position: map.getCenter(),
                    map: map
                });

                $('#id_place_location_temp').val(marker.getPosition().lat() + ',' + marker.getPosition().lng());
                google.maps.event.addListener(marker, 'position_changed', function() {
                    $('#id_place_location_temp').val(marker.getPosition().lat() + ',' + marker.getPosition().lng());
                });
            }
        });

        function searchPlaceLocation() {
            var address = placeModal.find('.search input').val();
            geocoder.geocode({'address': address}, function(results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    map.setCenter(results[0].geometry.location);
                    marker.setPosition(results[0].geometry.location);
                } else {
                    alert('Geocode was not successful for the following reason: ' + status);
                }
            });
        }

        placeModal.find('.search input').keypress(function(e) {
            if(e.which == 13) {
                searchPlaceLocation();
            }
        });

        placeModal.find('.search button').on('click', function() {
            searchPlaceLocation();
        });

        placeModal.find('.button-set-location').on('click', function() {
            var temp_input = $('#id_place_location_temp');
            $('.place-form .minimap').html('<img src="http://maps.googleapis.com/maps/api/staticmap?center=' + temp_input.val() + '&zoom=13&size=270x180&markers=color:red%7Clabel:S%7C' + temp_input.val() + '&sensor=false" />').show();
            $('#id_place_location').val(temp_input.val()).change();
            placeModal.modal('hide');
        });
    }

    function collect_data() {
        var data = {};

        if(form_title.data('dirty') || _is_very_dirty) {
            data['title'] = form_title.val();
            form_title.data('dirty', false);
        }

        form_activity = $('#control_activity_list');
        if(form_activity.data('dirty') || _is_very_dirty) {
            var activities = [];
            form_activity.find('input').each(function() {
                activities.push($(this).val());
            });

            if(activities) {
                data['activity'] = activities;
            }

            form_activity.data('dirty', false);
        }

        if(form_story.data('dirty') || _is_very_dirty) {
            data['story'] = form_story.redactor('get');
            form_story.data('dirty', false);
        }

        if(form_story.data('dirty') || _is_very_dirty) {
            data['story'] = form_story.redactor('get');
            form_story.data('dirty', false);
        }

        if(form_pictures_ordering.data('dirty') || _is_very_dirty) {
            data['picture_ordering'] = form_pictures_ordering.val();
            form_pictures_ordering.data('dirty', false);
        }

        if(form_topic.data('dirty') || _is_very_dirty) {
            data['topic'] = form_topic.find('option:selected').val();
            form_topic.data('dirty', false);
        }

        if(form_price.data('dirty') || _is_very_dirty) {
            data['price'] = form_price.val();
            form_price.data('dirty', false);
        }

        if(form_duration.data('dirty') || _is_very_dirty) {
            data['duration'] = form_duration.val();
            form_duration.data('dirty', false);
        }

        if(form_capacity.data('dirty') || _is_very_dirty) {
            data['capacity'] = form_capacity.val();
            form_capacity.data('dirty', false);
        }

        if(form_place.data('dirty') || _is_very_dirty) {
            var place_choice = form_place.find('input[name="place"]:checked').val();

            if(place_choice == 'system-place') {
                data['place-id'] = $('#id_place_system').find('option:selected').val();

            } else if(place_choice == 'userdefined-place') {
                data['place-id'] = $('#id_place_id').val();
                data['place-name'] = $('#id_place_name').val();
                data['place-address'] = $('#id_place_address').val();
                data['place-province'] = $('#id_place_province').find('option:selected').val();
                data['place-location'] = $('#id_place_location').val();
                data['place-direction'] = $('#id_place_direction').val();
            }

            form_place.data('dirty', false);
        }

        var is_data_empty = true;
        for (var key in data) {
            if(data.hasOwnProperty(key)) is_data_empty = false;
        }

        if(is_data_empty) {
            return null;
        } else {
            data['uid'] = workshop_uid;
            return data;
        }
    }

    function save_changes(submit_action, notify) {
        _is_saving = true;
        $('.form-footer .loading').show();
        $('.form-footer button').addClass('disabled');

        var data = collect_data();
        if(submit_action) data['submit'] = submit_action;

        if(data) {
            var jqxhr = $.post('/ajax/workshop/save/', data, function(response) {
                $('.form-footer .loading').hide();

                if(response.status == 'success') {
                    if(submit_action == 'draft' && window.location.pathname != response.data.edit_url) {
                        window.onbeforeunload = function() {};
                        window.location = response.data.edit_url;
                    } else {
                        $('.form-footer .preview').show();
                        $('.form-footer .preview a').attr('href', response.data.preview_url).attr('target', 'workshop-' + response.data.workshop_uid);
                        $('.form-content').trigger('saved');
                        if(notify) _notify('success', 'บันทึกเรียบร้อย', '');
                    }
                } else {
                    if(response.message) {
                        _notify('error', 'Cannot save', response.message);
                    } else {
                        _notify('error', 'Cannot save', 'Unknown error occurred');
                    }
                }
                _is_saving = false;
                _is_dirty = false;
                _is_very_dirty = false;
                _reset_form_header();

            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                $('.form-footer .loading').hide();
                _notify('error', 'Cannot save', errorThrown);
                _is_saving = false;
                _is_dirty = false;
                _is_very_dirty = false;
                _reset_form_header();
            });
        }
    }

    function _is_completed() {
        var is_completed = true;
        if(!form_title.val().trim()) is_completed = false;

        var has_activity_value = false;
        form_activity.find('input').each(function() {
            if($(this).val().trim()) has_activity_value = true;
        });

        if(!has_activity_value) is_completed = false;
        if(!form_story.redactor('get')) is_completed = false;
        if(!form_pictures.find('li.picture').length) is_completed = false;
        if(!$.isNumeric(form_price.val())) is_completed = false;
        if(!$.isNumeric(form_duration.val())) is_completed = false;
        if(!$.isNumeric(form_capacity.val())) is_completed = false;
        if(!form_topic.val().trim()) is_completed = false;

        var place_type = form_place.find('input[name="place-type"]:checked').val();
        if(place_type == 'system-place') {
            if(!$('#id_place_system').find('option:selected').val()) is_completed = false;
        } else if(place_type == 'userdefined-place') {
            if(!$('#id_place_name').val().trim() ||
                    !$('#id_place_address').val().trim() ||
                    !$('#id_place_province').find('option:selected').val() ||
                    !$('#id_place_location').val().trim() ||
                    !$('#id_place_direction').val().trim()) {
                is_completed = false;
            }
        } else {
            is_completed = false;
        }

        return is_completed;
    }

    function _reset_form_header() {
        var is_completed = _is_completed();
        //$('.form-footer .button-draft').prop('disabled', !_is_dirty);

        $('.form-footer .button-draft').removeClass('disabled');

        if(is_completed) {
            $('.form-footer .button-submit').removeClass('disabled').tooltip('destroy');
        } else {
            $('.form-footer .button-submit').addClass('disabled').tooltip({title: 'ยังกรอกข้อมูลไม่ครบถ้วน',trigger: 'hover'});
        }
    }

    function _start_autosave_timer() {
        autosave_timer = window.setTimeout(function() {
            if(_is_dirty && !_is_saving) {
                save_changes();
                _start_autosave_timer();
            } else {
                autosave_timer = null;
            }
        }, 20000);
    }

    function set_dirty() {
        _is_dirty = true;
        _reset_form_header();

        if(enable_autosave) {
            if(!autosave_timer) {
                save_changes();
                _start_autosave_timer();
            }
        }

        if(page_type == 'create') {
            window.onbeforeunload = function() {return 'Please save your draft before reloading this page';};
        } else if(page_type == 'edit') {
            window.onbeforeunload = function() {
                if(_is_dirty || _is_saving) {
                    return 'Please save your data before reloading this page';
                }
            };
        }
    }

    form_title.on('change', function() {
        $('#id_title').data('dirty', true);
        set_dirty();
    });

    _init_workshop_activities();

    form_activity.find('input').on('change', function() {
        form_activity.data('dirty', true);
        set_dirty();
    });

    form_story.on('redactor-keyup', function() {
        form_story.data('dirty', true);
        set_dirty();
    });

    _init_pictures();

    form_topic.on('change', function() {
        form_topic.data('dirty', true);
        set_dirty();
    });

    form_price.on('change', function() {
        form_price.removeClass('error');
        if(!$.isNumeric(form_price.val())) {
            form_price.addClass('error');
        } else if(parseInt(form_price.val(), 10) < 50) {
            form_price.addClass('error');
        } else {
            form_price.data('dirty', true);
            set_dirty();
        }
    });

    form_duration.on('change', function() {
        form_duration.removeClass('error');
        if(!$.isNumeric(form_duration.val())) {
            form_duration.addClass('error');
        } else {
            form_duration.data('dirty', true);
            set_dirty();
        }
    });

    form_capacity.on('change', function() {
        form_capacity.removeClass('error');
        if(!$.isNumeric(form_capacity.val())) {
            form_capacity.addClass('error');
        } else {
            form_capacity.data('dirty', true);
            set_dirty();
        }
    });

    _init_place();

    form_place.find('input[name="place"]').on('change', function() {
        form_place.data('dirty', true);
        set_dirty();
    });

    $('#id_place_system').on('change', function() {
        form_place.find('input[value="system-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });

    /*
    // SELECT HAS ALREADY BINDED TO SET DIRTY
    $('#id_place_userdefined').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });*/

    $('#id_place_name').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });

    $('#id_place_address').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });

    $('#id_place_province').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });

    $('#id_place_location').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });

    $('#id_place_direction').on('change', function() {
        form_place.find('input[value="userdefined-place"]').trigger('click');
        form_place.data('dirty', true);
        set_dirty();
    });
}