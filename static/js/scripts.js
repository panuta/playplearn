
$(document).ready(function() {
    $('.modal').on('shown', function(){
        $('body').css('overflow', 'hidden');
    }).on('hidden', function(){
        $('body').css('overflow', 'auto');
    });
});

function initCourseCreatePage() {
    $('.form-nav a').on('click', function() {
        $('.form-content .form-content-panel').hide();
        $('.form-nav li').removeClass('active');
        $($(this).attr('href')).show();
        $(this).parent().addClass('active');
        return false;
    });


    // Details

    $("#id_topics").select2();

    $('#id_story').redactor();

    $('.capacity-control input').slider();

    //$('#modal-course-submitted').modal();
}