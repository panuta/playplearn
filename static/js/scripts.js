
$(document).ready(function() {
    $('.modal').on('shown', function(){
        $('body').css('overflow', 'hidden');
    }).on('hidden', function(){
        $('body').css('overflow', 'auto');
    });
});

function initCourseModifyPage() {
    $('.form-navigation a').on('click', function() {
        $('.form-content .form-content-panel').hide();
        $('.form-navigation li').removeClass('active');
        $($(this).attr('href')).show();
        $(this).parent().addClass('active');
        return false;
    });

    /*
    $('input').keypress(function(e) {
        if(e.which == 13) {
            e.preventDefault();
        }
    });*/

    // Form Actions
    $('.form-actions .button-draft').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;
        autosave('', function(response) {
            window.location = response.data.edit_url;
        });
        return false;
    });

    $('.form-actions .button-submit').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;
        autosave('submit', function(response) {
            $('#modal-course-submitted').modal();
        });
        return false;
    });

    $('.form-actions .button-discard').on('click', function() {
        var jqxhr = $.post('/ajax/course/discard/', {uid:_course_uid}, function(response) {
            if(response.status == 'success') {
                window.location = response.data.edit_url;
            } else {
                if(response.message) {
                    _autosave_error('Cannot save: ' + response.message);
                } else {
                    _autosave_error('Cannot save: Unknown error');
                }
            }
        }, 'json');

        jqxhr.error(function(jqXHR, textStatus, errorThrown) {
            _autosave_error('Cannot save: ' + errorThrown);
        });
    });

    $('.form-actions .button-update').on('click', function() {
        _is_dirty = true;
        _is_very_dirty = true;
        autosave('update');
        return false;
    });

    // Initialize Course Outline
    function _init_course_outline() {
        function _add_new_outline() {
            var new_outline = $('<li class="outline"><i class="icon-remove"></i><i class="icon-reorder"></i><input type="text"/></li>');
            _set_outline_events(new_outline);
            new_outline.insertBefore($('#control_add_outline').parent());
            new_outline.find('input').focus();
        }

        $('#control_add_outline').on('click', function() {
            _add_new_outline();
            return false;
        });

        function _set_outline_events(outline_object) {
            outline_object.find('.icon-remove').popover({
                html: true,
                placement: 'left',
                content: '<a href="#" class="btn btn-mini btn-danger button-outline-remove">Confirm delete</a> <a href="#" class="btn btn-mini button-outline-remove-cancel">Cancel</a>'
            });

            outline_object.find('input').on('change', function() {
                _set_outline_dirty();
            });

            outline_object.find('input').keypress(function(e) {
                if(e.which == 13) {
                    var next_outline = $(this).closest('.outline').next('.outline');

                    if(next_outline.length) {
                        next_outline.find('input').focus();
                    } else {
                        _add_new_outline();
                    }
                }
            });
        }

        function _set_outline_dirty() {
            form_outline.data('dirty', true);
            set_dirty();
        }

        form_outline.sortable({
            distance: 15,
            handle: '.icon-reorder',
            items: 'li.outline',
            placeholder: 'ui-state-highlight',
            tolerance: 'pointer',
            stop: function( event, ui ) {
                _set_outline_dirty();
            }
        });

        $(document).on('click', '.popover .button-outline-remove', function() {
            var outlineObject = $(this).closest('.outline');
            outlineObject.remove();
            _set_outline_dirty();
            return false;
        });

        $(document).on('click', '.popover .button-outline-remove-cancel', function() {
            $(this).closest('.outline').find('.icon-remove').popover('hide');
            return false;
        });

        _set_outline_events($('#control_outline_list'));
    }

    // Initialize Pictures
    function _init_pictures_and_cover() {
        var cover_form = $('#id_cover');
        var upload_cover = $('#upload-cover');
        cover_form.fileupload({
            dataType: 'json',
            url: '/ajax/course/cover/upload/',
            formData: function (form) {return [{name:'uid', value:_course_uid}, {name:'csrfmiddlewaretoken', value: csrftoken}];},
            add: function (e, data) {
                $('.form-actions button').attr('disabled', true);

                var file = data.files[0];

                if(typeof file.type != 'undefined' && file.type.indexOf('image/') != 0) {
                    upload_cover.html('<div class="error">This is not an image file</div>').show();
                } else if(file.size > 3000000) {
                    upload_cover.html('<div class="error">Image file size is too large<br/>(Max 3 megabytes)</div>').show();
                } else {
                    upload_cover.html('<div class="progress progress-striped"><div class="bar"></div></div>').show();
                    cover_form.attr('disabled', true);
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

                cover_form.attr('disabled', false);

                var response = data.result;

                if(response.status == 'success') {
                    upload_cover.html('<img src="' + response.data.cover_url + '" height="100" width="275" />');
                    $('#id_cover_filename').val(response.data.cover_filename);
                    _set_completeness(response.data.completeness)

                } else if(response.status == 'error') {
                    if(response.message) {
                        upload_cover.html('<div class="error">' + response.message + '</div>')
                    } else {
                        upload_cover.html('<div class="error">Unknown error</div>')
                    }
                }

                _reset_action_buttons();
            },
            fail: function (e, data) {
                upload_cover.html('<div class="error">Upload error</div>')
                _reset_action_buttons();
            }
        });
        cover_form.attr('disabled', false);

        var upload_pictures = $('#upload-pictures');
        var upload_pictures_ordering = $('#id_pictures_ordering');
        $('#id_pictures').fileupload({
            dataType: 'json',
            url: '/ajax/course/picture/upload/',
            sequentialUploads: true,
            formData: function (form) {return [{name:'uid', value:_course_uid}, {name:'csrfmiddlewaretoken', value: csrftoken}, {name:'ordering', value: upload_pictures_ordering.val()}];},
            add: function (e, data) {
                $('.form-actions button').attr('disabled', true);

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
                    data.context.html('<div class="image"><i class="icon-reorder"></i><img src="' + response.data.picture_url + '" /></div><div class="description"><label>Describe this picture <input type="text" /></label><a href="#" class="delete">Delete picture</a></div>');
                    data.context.attr('media-uid', response.data.media_uid);

                    _set_picture_events(data.context);
                    _set_completeness(response.data.completeness)

                } else if(response.status == 'error') {
                    data.context.removeClass('uploading').addClass('error');

                    if(response.message) {
                        data.context.html('<em>' + response.message + '</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                    } else {
                        data.context.html('<em>Unknown error</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                    }
                }

                _reset_action_buttons();
            },
            fail: function (e, data) {
                if (data.errorThrown == 'abort') {
                    data.context.remove();
                } else {
                    data.context.removeClass('uploading').addClass('error');
                    data.context.html('<em>Upload error</em><div class="dismiss"><a href="#">Dismiss</a></div>');
                }
                _reset_action_buttons();
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
                    new_ordering = new_ordering + $(this).attr('media-uid') + ',';
                });
                upload_pictures_ordering.val(new_ordering);

                upload_pictures_ordering.data('dirty', true);
                set_dirty();
            }
        });

        $(document).on('click', '.button-picture-remove', function() {
            $('.form-actions button').attr('disabled', true);

            if($(this).hasClass('disabled')) {
                return false;
            }

            var delete_link = $(this).closest('.description').find('.delete');
            var delete_actions = $(this).closest('.popover-content').find('a');
            delete_actions.addClass('disabled');

            var media_uid = $(this).closest('li.picture').attr('media-uid');
            var jqxhr = $.post('/ajax/course/picture/delete/', {uid: _course_uid, media_uid: media_uid}, function(response) {
                if(response.status == 'success') {
                    upload_pictures_ordering.val(response.data.ordering);
                    upload_pictures.find('li[media-uid=' + media_uid + ']').fadeOut(function() {
                        $(this).remove();
                    });
                    _set_completeness(response.data.completeness);

                } else {
                    if(response.message) {
                        _modal_error_message('Delete error', response.message, function() {
                            delete_actions.removeClass('disabled');
                            delete_link.popover('hide');
                        });
                    } else {
                        _modal_error_message('Delete error', 'Unknown error', function() {
                            delete_actions.removeClass('disabled');
                            delete_link.popover('hide');
                        });
                    }
                }

                _reset_action_buttons();
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                _modal_error_message('Cannot delete picture', 'Unexpected error occurred: ' + errorThrown, function() {
                    delete_actions.removeClass('disabled');
                    delete_link.popover('hide');
                });
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

    // Initialize Place
    function _init_place() {
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
                    zoom = 12;
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
            $('.place-input-location .location_latlng').text(temp_input.val());
            $('#id_place_location').val(temp_input.val()).change();
            placeModal.modal('hide');
        });
    }

    //$('#modal-course-submitted').modal();

    var form_title = $('#id_title');
    var form_outline = $('#control_outline_list');
    var form_story = $('#id_story');
    var form_cover = $('#cover_filename');
    var form_pictures = $('#upload-pictures');
    var form_pictures_ordering = $('#id_pictures_ordering');
    var form_school = $('#id_school');
    var form_topics = $('#id_topics');
    var form_level = $('#id_level');
    var form_price = $('#id_price');
    var form_duration = $('#id_duration');
    var form_capacity = $('#id_capacity');
    var form_place = $('#content-place');

    var _is_saving = false;
    var _is_very_dirty = false;
    var _is_dirty = false;
    var autosave_timer = null;

    function autosave(next_action, callback) {
        _is_saving = true;
        $('.form-actions .message').html('<span class="loading"><img src="/static/images/ui/loading.gif" /></span>');
        $('.form-actions button').attr('disabled', true);

        _is_dirty = false;
        var data = {};

        if(form_title.data('dirty') || _is_very_dirty) {
            data['title'] = form_title.val();
            form_title.data('dirty', false);
        }

        form_outline = $('#control_outline_list');
        if(form_outline.data('dirty') || _is_very_dirty) {
            var outlines = [];
            form_outline.find('input').each(function() {
                outlines.push($(this).val());
            });

            if(outlines) {
                data['outline'] = outlines;
            }

            form_outline.data('dirty', false);
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
            var media_desc = [];
            form_pictures.find('li.picture').each(function() {
                media_desc.push({uid: $(this).attr('media-uid'), description: $(this).find('input').val()});
            });

            if(media_desc) {
                data['media_desc'] = media_desc;
            }

            form_pictures.data('dirty', false);
        }

        if(form_pictures_ordering.data('dirty') || _is_very_dirty) {
            data['media_ordering'] = form_pictures_ordering.val();
            form_pictures_ordering.data('dirty', false);
        }

        if(form_school.data('dirty') || _is_very_dirty) {
            data['school'] = form_school.find('option:selected').val();
            form_school.data('dirty', false);
        }

        if(form_topics.data('dirty') || _is_very_dirty) {
            data['topics'] = form_topics.val();
            form_topics.data('dirty', false);
        }

        if(form_level.data('dirty') || _is_very_dirty) {
            data['level'] = form_level.find('option:selected').val();
            form_level.data('dirty', false);
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
            var place_choice = form_place.find('.place-label input:checked').val();
            data['place'] = place_choice;

            if(place_choice == 'defined-place') {
                data['place-defined'] = $('#id_place_defined').find('option:selected').val();

            } else if(place_choice == 'userdefined-place') {
                data['place-name'] = $('#id_place_name').val();
                data['place-phone'] = $('#id_place_phone').val();
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

        if(!is_data_empty) {
            data['uid'] = _course_uid;

            if(next_action != undefined) {
                data['next_action'] = next_action;
            }

            var jqxhr = $.post('/ajax/course/autosave/', data, function(response) {
                if(response.status == 'success') {
                    $('.form-actions .message').html('<span class="preview"><i class="icon-external-link-sign"></i> <a href="' + response.preview_url + '" class="link-preview">See preview</a></span>');
                } else {
                    if(response.message) {
                        _autosave_error('Cannot save: ' + response.message);
                    } else {
                        _autosave_error('Cannot save: Unknown error');
                    }
                }

                if(callback != undefined) {
                    callback(response);
                } else {
                    _after_autosave(response);
                }
            }, 'json');

            jqxhr.error(function(jqXHR, textStatus, errorThrown) {
                _autosave_error('Cannot save: ' + errorThrown);

                if(callback == undefined) {
                    _after_autosave();
                }
            });
        }
        _is_very_dirty = false;
    }

    function _autosave_error(message) {
        $('.form-actions .message').html('<span class="error-message">' + message + '</span>');
    }

    function _set_completeness(completeness) {
        $('.completeness .bar').css('width', completeness + '%');
        $('.completeness .percentage').text(completeness + '%');
    }

    function _reset_action_buttons() {
        $('.form-actions .button-draft').attr('disabled', false);
        $('.form-actions .button-submit').attr('disabled', !is_publishable());
        $('.form-actions .button-discard').attr('disabled', false);
        $('.form-actions .button-update').attr('disabled', !is_publishable());
    }

    function _after_autosave(response) {
        if(response && response.data && response.data.completeness) {
            _set_completeness(response.data.completeness);
        }

        _reset_action_buttons();
        _is_saving = false;
    }

    function is_publishable() {
        var publishable = true;
        if(!form_title.val().trim()) publishable = false;

        var has_value = false;
        form_outline.find('input').each(function() {
            if($(this).val().trim()) has_value = true;
        });
        publishable = has_value;

        if(!form_story.redactor('get')) publishable = false;

        if(!form_cover.val()) publishable = false;
        if(!form_pictures.find('li.picture').length) publishable = false;

        if(!form_school.val().trim()) publishable = false;
        if(!form_topics.val().trim()) publishable = false;
        if(!form_level.val().trim()) publishable = false;
        if(!$.isNumeric(form_price.val())) publishable = false;
        if(!$.isNumeric(form_duration.val())) publishable = false;
        if(!$.isNumeric(form_capacity.val())) publishable = false;

        var place_choice = form_place.find('.place-label input:checked').val();
        if(!place_choice.trim()) publishable = false;

        if(place_choice == 'defined-place') {
            if(!$('#id_place_defined').find('option:selected').val().trim()) publishable = false;

        } else if(place_choice == 'userdefined-place') {
            if(!$('#id_place_name').val().trim()) publishable = false;
            if(!$('#id_place_phone').val().trim()) publishable = false;
            if(!$('#id_place_address').val().trim()) publishable = false;
            if(!$('#id_place_province').find('option:selected').val().trim()) publishable = false;
            if(!$('#id_place_location').val().trim()) publishable = false;
            if(!$('#id_place_direction').val().trim()) publishable = false;
        }

        return publishable;
    }

    function _start_autosave_timer() {
        autosave_timer = window.setTimeout(function() {
            if(_is_dirty && !_is_saving) {
                autosave();
                _start_autosave_timer();
            } else {
                autosave_timer = null;
            }
        }, 20000);
    }

    function set_dirty() {
        _is_dirty = true;
        _reset_action_buttons();

        if(!autosave_timer) {
            autosave();
            _start_autosave_timer();
        }
    }

    form_title.on('change', function() {
        $('#id_title').data('dirty', true);
        set_dirty();
    });

    _init_course_outline();

    form_outline.find('input').on('change', function() {
        form_outline.data('dirty', true);
        set_dirty();
    });

    form_story.redactor({
        minHeight: 300,
        toolbarFixed: true,
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

    form_topics.select2({
        formatNoMatches: function(term) {return 'Enter your topics'},
        tags: [],
        tokenSeparators: [","],
        width: 'copy'
    }).on('change', function() {
            form_topics.data('dirty', true);
            set_dirty();
        });

    form_level.on('change', function() {
        form_level.data('dirty', true);
        set_dirty();
    });

    form_price.on('change', function() {
        form_price.removeClass('error');
        if(!$.isNumeric(form_price.val())) {
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

    form_place.find('.place-label input').on('change', function() {
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_defined').on('change', function() {
        form_place.find('.place-label input[value="defined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_name').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_phone').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_address').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_province').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_location').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    $('#id_place_direction').on('change', function() {
        form_place.find('.place-label input[value="userdefined-place"]').trigger('click');
        $('#content-place').data('dirty', true);
        set_dirty();
    });

    form_title.focus();
}