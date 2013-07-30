
/*
$(document).ready(function() {
    $('.modal').on('shown', function(){
        $('body').css('overflow', 'hidden');
    }).on('hidden', function(){
        $('body').css('overflow', 'auto');
    });
});*/

function initCourseModifyPage(course_uid, enable_autosave, page_type) {
    var form_title = $('#id_title');
    var form_activity = $('#control_activity_list');
    var form_story = $('#id_story');
    var form_cover = $('#id_cover_filename');
    var form_pictures = $('#upload-pictures');
    var form_pictures_ordering = $('#id_pictures_ordering');
    var form_school = $('#id_school');
    var form_price = $('#id_price');
    var form_duration = $('#id_duration');
    var form_capacity = $('#id_capacity');
    var form_place = $('#id_place');

    var _is_saving = false;
    var _is_very_dirty = false;
    var _is_dirty = false;
    var autosave_timer = null;

    // BINDING FORM ACTIONS

    $('.form-footer .button-draft').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;
        save_changes('draft', true);
        return false;
    });

    $('.form-footer .button-submit-approval').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;

        $('.form-content').one('saved', function(e, response) {
            $('#modal-course-submitted').modal();
        });

        save_changes('approval', false);
        return false;
    });

    $('.form-footer .button-save-changes').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;
        save_changes('update', true);
        return false;
    });

    if(page_type == 'create') {
        window.onbeforeunload = function() {
            return 'Please save your draft before reloading this page';
        };
    } else if(page_type == 'edit') {
        window.onbeforeunload = function() {
            if(_is_dirty || _is_saving) {
                return 'Please save your data before reloading this page';
            }
        };
    }

    // Initialize Course Activities
    function _init_course_activities() {
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
    function _init_pictures_and_cover() {
        var cover_form = $('#id_cover');
        var upload_cover = $('#upload-cover');
        cover_form.fileupload({
            dataType: 'json',
            url: '/ajax/course/cover/upload/',
            formData: function (form) {return [{name:'uid', value:course_uid}, {name:'csrfmiddlewaretoken', value: csrftoken}];},
            add: function (e, data) {
                $('.form-footer button').prop('disabled', true);

                var file = data.files[0];

                if(typeof file.type != 'undefined' && file.type.indexOf('image/') != 0) {
                    upload_cover.html('<div class="error">This is not an image file</div>').show();
                } else if(file.size > 3000000) {
                    upload_cover.html('<div class="error">Image file size is too large<br/>(Max 3 megabytes)</div>').show();
                } else {
                    upload_cover.html('<div class="progress progress-striped"><div class="bar"></div></div>').show();
                    cover_form.prop('disabled', true);
                    data.submit();
                }
            },
            progress: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                upload_cover.find('.bar').attr('data-percentage', progress);
                upload_cover.find('.bar').progressbar({display_text: 1});
            },
            done: function (e, data) {
                upload_cover.find('.bar').attr('data-percentage', 100);
                upload_cover.find('.bar').progressbar({display_text: 1});

                cover_form.prop('disabled', false);

                var response = data.result;

                if(response.status == 'success') {
                    upload_cover.html('<img src="' + response.data.cover_url + '" height="130" width="255" />');
                    $('#id_cover_filename').val(response.data.cover_filename);

                } else if(response.status == 'error') {
                    if(response.message) {
                        upload_cover.html('<div class="error">' + response.message + '</div>')
                    } else {
                        upload_cover.html('<div class="error">Unknown error</div>')
                    }
                }

                _reset_form_header();
            },
            fail: function (e, data) {
                upload_cover.html('<div class="error">Upload error</div>')
                _reset_form_header();
            }
        });
        cover_form.prop('disabled', false);

        var upload_pictures = $('#upload-pictures');
        var upload_pictures_ordering = $('#id_pictures_ordering');
        $('#id_pictures').fileupload({
            dataType: 'json',
            url: '/ajax/course/picture/upload/',
            sequentialUploads: true,
            formData: function (form) {return [{name:'uid', value:course_uid}, {name:'csrfmiddlewaretoken', value: csrftoken}, {name:'ordering', value: upload_pictures_ordering.val()}];},
            add: function (e, data) {
                $('.form-footer button').prop('disabled', true);

                var file = data.files[0];
                var errorObject = null;

                if(typeof file.type != 'undefined' && file.type.indexOf('image/') != 0) {
                    errorObject = $('<li class="error"><em>Image file only</em><div class="dismiss"><a href="#">Dismiss</a></div></li>');
                } else if(file.size > 5000000) {
                    errorObject = $('<li class="error"><em>Image is too big<br/>(Max 5 megabytes)</em><div class="dismiss"><a href="#">Dismiss</a></div></li>');
                }

                if(errorObject) {
                    upload_pictures.append(errorObject);
                    return;
                }

                var uploadingObject = $('<li class="uploading"><em>Uploading...</em><div class="progress progress-striped"><div class="bar"></div></div></li>');
                upload_pictures.append(uploadingObject);

                uploadingObject.data('data', data);
                data.context = uploadingObject;

                data.submit();
            },
            progress: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                data.context.find('.bar').attr('data-percentage', progress);
                data.context.find('.bar').progressbar({display_text: 1});
            },
            done: function (e, data) {
                data.context.find('.bar').attr('data-percentage', 100);
                data.context.find('.bar').progressbar({display_text: 1});

                var file = data.files[0];
                var response = data.result;

                if(response.status == 'success') {
                    upload_pictures_ordering.val(response.data.ordering);

                    data.context.removeClass('uploading').addClass('picture');
                    data.context.html('<div class="image"><i class="icon-reorder"></i><img src="' + response.data.picture_url + '" /></div><div class="description"><label>คำอธิบายรูปภาพ <input type="text" /></label><a href="#" class="delete">ลบรูป</a></div>');
                    data.context.attr('picture-uid', response.data.picture_uid);

                    _set_picture_events(data.context);

                } else if(response.status == 'error') {
                    data.context.removeClass('uploading').addClass('error');

                    if(response.message) {
                        data.context.html('<em>' + response.message + '</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                    } else {
                        data.context.html('<em>Unknown error</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                    }
                }

                _reset_form_header();
            },
            fail: function (e, data) {
                if (data.errorThrown == 'abort') {
                    data.context.remove();
                } else {
                    data.context.removeClass('uploading').addClass('error');
                    data.context.html('<em>Upload error</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                }
                _reset_form_header();
            }
        });

        function _set_picture_events(picture_object) {
            picture_object.find('.delete').popover({
                html: true,
                placement: 'left',
                content: '<a href="#" class="btn btn-mini btn-danger button-picture-remove">Confirm delete</a> <a href="#" class="btn btn-mini button-picture-remove-cancel">Cancel</a>'
            }).on('click', function() {
                return false;
            });

            picture_object.find('.description input').on('change', function() {
                upload_pictures.data('dirty', true);
                set_dirty();
            });
        }

        upload_pictures.sortable({
            distance: 15,
            handle: '.image',
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

        $(document).on('click', '.button-picture-remove', function() {
            $('.form-footer button').prop('disabled', true);

            if($(this).hasClass('disabled')) {
                return false;
            }

            var delete_link = $(this).closest('.description').find('.delete');
            var delete_actions = $(this).closest('.popover-content').find('a');
            delete_actions.addClass('disabled');

            var picture_uid = $(this).closest('li.picture').attr('picture-uid');
            var jqxhr = $.post('/ajax/course/picture/delete/', {uid: course_uid, picture_uid: picture_uid}, function(response) {
                if(response.status == 'success') {
                    upload_pictures_ordering.val(response.data.ordering);
                    upload_pictures.find('li[picture-uid=' + picture_uid + ']').fadeOut(function() {
                        $(this).remove();
                    });
                } else {
                    delete_actions.removeClass('disabled');
                    delete_link.popover('hide');

                    if(response.message) {
                        _alertModal('error', 'Delete error', response.message);
                    } else {
                        _alertModal('error', 'Delete error', 'Unknown error');
                    }
                }

                _reset_form_header();
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                delete_actions.removeClass('disabled');
                delete_link.popover('hide');
                _alertModal('error', 'Delete error', 'Unexpected error occurred: ' + errorThrown);
            });

            return false;
        });

        $(document).on('click', '.button-picture-remove-cancel', function() {
            if($(this).hasClass('disabled')) {
                return false;
            }

            $(this).closest('li.picture').find('.delete').popover('hide');
            return false;
        });

        $(document).on('click', '#upload-pictures li.error .dismiss a', function() {
            $(this).closest('li.error').remove();
            return false;
        });

        _set_picture_events(upload_pictures);
    }

    // Initialize Topic
    function format(topic) {
        var topicObj = topic.element;
        console.log($(topicObj).data('desc'));
        return '<span class="topic"><strong>' + topic.text + '</strong><br/>' + $(topicObj).data('desc') + '</span>';
    }

    form_school.select2({
        allowClear: true,
        minimumResultsForSearch: 1000,
        formatResult: format,
        width: 350,
        escapeMarkup: function(m) { return m; }
    });

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

                var jqxhr = $.get('/ajax/course/place/get/', {place_id:selected}, function(response) {
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

        if(form_pictures.data('dirty') || _is_very_dirty) {
            var picture_desc = [];
            form_pictures.find('li.picture').each(function() {
                picture_desc.push({uid: $(this).attr('picture-uid'), description: $(this).find('input').val()});
            });

            if(picture_desc) {
                data['picture_descriptions'] = picture_desc;
            }

            form_pictures.data('dirty', false);
        }

        if(form_pictures_ordering.data('dirty') || _is_very_dirty) {
            data['picture_ordering'] = form_pictures_ordering.val();
            form_pictures_ordering.data('dirty', false);
        }

        if(form_school.data('dirty') || _is_very_dirty) {
            data['school'] = form_school.find('option:selected').val();
            form_school.data('dirty', false);
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
            data['uid'] = course_uid;
            return data;
        }
    }

    function save_changes(submit_action, notify) {
        _is_saving = true;
        $('.form-footer .loading').show();
        $('.form-footer button').prop('disabled', true);

        var data = collect_data();
        if(submit_action) data['submit'] = submit_action;

        if(data) {
            var jqxhr = $.post('/ajax/course/save/', data, function(response) {
                $('.form-footer .loading').hide();

                if(response.status == 'success') {
                    if(submit_action == 'draft' && window.location.pathname != response.data.edit_url) {
                        window.onbeforeunload = function() {};
                        window.location = response.data.edit_url;
                    } else {
                        $('.form-footer .preview').show();
                        $('.form-footer .preview a').attr('href', response.data.preview_url).attr('target', 'course-' + response.data.course_uid);
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

        if(!form_cover.val()) is_completed = false;
        if(!form_pictures.find('li.picture').length) is_completed = false;

        if(!form_school.val().trim()) is_completed = false;
        if(!$.isNumeric(form_price.val())) is_completed = false;
        if(!$.isNumeric(form_duration.val())) is_completed = false;
        if(!$.isNumeric(form_capacity.val())) is_completed = false;

        var place_choice = form_place.find('input[name="place"]:checked').val();
        if(place_choice == 'system-place') {
            if(!$('#id_place_system').find('option:selected').val()) is_completed = false;
        } else if(place_choice == 'userdefined-place') {
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
        $('.form-footer .button-draft').prop('disabled', false);
        $('.form-footer .button-submit').prop('disabled', !is_completed);
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
    }

    form_title.on('change', function() {
        $('#id_title').data('dirty', true);
        set_dirty();
    });

    _init_course_activities();

    form_activity.find('input').on('change', function() {
        form_activity.data('dirty', true);
        set_dirty();
    });

    form_story.redactor({
        minHeight: 200,
        buttons: ['html', '|', 'bold', 'italic', 'deleted', '|',
            'unorderedlist', 'orderedlist', '|', 'link', '|'],
        keyupCallback: function(e) {
            form_story.data('dirty', true);
            set_dirty();
        }
    });

    _init_pictures_and_cover();

    form_school.on('change', function() {
        form_school.data('dirty', true);
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