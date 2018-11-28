$.ajaxSetup({
    beforeSend: function (xhr, settings) {
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

        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

$(document).ready(function () {
    $(".alert-success").delay(1500).slideUp(300);
    $(".alert-error").delay(1500).slideUp(300);

    $("#training_type").change(function () {
        var value = $(this).find(":selected").text();
        if (value == "Until accuracy threshold achieved"){
            $(".percent").show()
        }else{
            $(".percent").hide()
        }
    });
    
    $(".answer").click(function () {
        $(".btn_answer").removeAttr('disabled');
    });

    $(".btn_answer").click(function () {
        $(".answer").attr('disabled', true);

        var el = $("[name='answer']:checked");
        $(el).attr('disabled', false);

        $.each($(".answer"), function (i, e) {
            var tr = $(e).data('true')
            if (tr === 'True') {
                $(e).parent().css({'color': 'green'});
            } else {
                $(e).parent().css({'color': 'red'});
            }
        });

        $.ajax({
            type: "POST",
            data: $(".form").serialize(),
            url: $(".form").attr('action'),
            success: function (data) {
                console.log(data)
                // if (data.status == True)
                $(".result").html(data.message);
                $(".btn_answer").hide();

                if (data.congratulation){
                    $(".congratulation").show()
                    $(".congratulation_text").text(data.congratulation)
                    $(".video_viewed").text(data.video_viewed)
                    $(".overall_accuracy").text(data.overall_accuracy)
                }else {
                    if (data.end_session == false){
                        $(".next_video").show();
                        $(".close_session").show();
                    }else{
                        $("#id_form").show()
                        // $(".another_session").show();
                        // $(".see_result").show();
                    }
                }

            }
        })
    });

    $(".next_video").click(function () {
        location.reload();
    })
});


