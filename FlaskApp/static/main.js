$(document).ready(function () {
    $('#addFriendForm').on('submit', function (event) {
        event.preventDefault();

        var req = new XMLHttpRequest()
        req.onreadystatechange = function () {
            if (req.readyState == 4 && req.status == 200) {
                alert(JSON.parse(req.responseText).msg);
            }
        }

        req.open('POST', '/add_friend')
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
        var postVars = 'handler=' + $("#friendHandlerInput").val()
        req.send(postVars)

        // $.ajax({
        //     data: {
        //         handler: $("#friendHandlerInput").val()
        //     },
        //     type: "POST",
        //     url: "/add_friend"
        // });

    });

    $('.remove_friend_btn').on('click', function () {
        var elm = $(this).parent().parent();
        var _id = elm.data('id');
        if (_id != null) {
            $.ajax({
                data: {
                    id: _id
                },
                type: 'POST',
                url: "/remove_friend"
            }).done(function (data) {
                if (data.msg == "success") {
                    elm.remove();
                } else {
                    alert("Not successfull");
                }
            })
        }


    });
});

