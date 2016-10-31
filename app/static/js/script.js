/**
 * Created by praateek on 30/10/16.
 */
//plugin bootstrap minus and plus
//http://jsfiddle.net/laelitenetwork/puJ6G/
$('.btn-number').click(function(e){
    e.preventDefault();

    fieldName = $(this).attr('data-field');
    type      = $(this).attr('data-type');
    var input = $("input[name='"+fieldName+"']");
    var currentVal = parseInt(input.val());
    console.log(currentVal);
    if (!isNaN(currentVal)) {
        if(type == 'minus') {

            if(currentVal > input.attr('min')) {
                input.val(currentVal - 1).change();
            }
            if(parseInt(input.val()) == input.attr('min')) {
                $(this).attr('disabled', true);
            }

        } else if(type == 'plus') {

            if(currentVal < input.attr('max')) {
                input.val(currentVal + 1).change();
            }
            if(parseInt(input.val()) == input.attr('max')) {
                $(this).attr('disabled', true);
            }

        }
    } else {
        input.val(0);
    }
});
$('.input-number').focusin(function(){
   $(this).data('oldValue', $(this).val());
});
$('.input-number').change(function() {

    minValue =  parseInt($(this).attr('min'));
    maxValue =  parseInt($(this).attr('max'));
    valueCurrent = parseInt($(this).val());

    name = $(this).attr('name');
    if(valueCurrent >= minValue) {
        $(".btn-number[data-type='minus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the minimum value was reached');
        $(this).val($(this).data('oldValue'));
    }
    if(valueCurrent <= maxValue) {
        $(".btn-number[data-type='plus'][data-field='"+name+"']").removeAttr('disabled')
    } else {
        alert('Sorry, the maximum value was reached');
        $(this).val($(this).data('oldValue'));
    }


});
$(".input-number").keydown(function (e) {
        // Allow: backspace, delete, tab, escape, enter and .
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 190]) !== -1 ||
             // Allow: Ctrl+A
            (e.keyCode == 65 && e.ctrlKey === true) ||
             // Allow: home, end, left, right
            (e.keyCode >= 35 && e.keyCode <= 39)) {
                 // let it happen, don't do anything
                 return;
        }
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });

$(".addproduct").on('click',function(a,b){
    var sid = $.cookie("sessionuid")
    var pid = $(this).attr('data-pid');
    var value = $("input[name='quant']").val();
    if(value != 'undefined')
    {
        postAjax('/api/updatecart',sid,pid,value)
    }
    else{
         postAjax('/api/updatecart',sid,pid)
    }
    console.log(sid)
});

$(".removeproduct").on('click',function(a,b){
    var pid = $(this).attr('data-pid');
    postAjax('/api/updatecart',pid,'delete')

});

function postAjax(url,attribute1,attribute2,attribute3=''){
        var furl = url;
        console.log(furl)
        $.ajax({
            type: 'POST',
            url: furl,
            data: JSON.stringify({sid:attribute1, pid:attribute2, v:attribute3}), // or JSON.stringify ({name: 'jonas'}),
            success: function(a) {
                if(a.status=="error"){
                    $("#alertbox").removeClass("alert-warning")
                    $("#alertbox").removeClass("alert-success");

                    $("#alertbox").addClass("alert-danger");
                    $("#alertbox").html(a.message)

                }
                else if(a.status=="warning"){
                    $("#alertbox").removeClass("alert-danger")
                    $("#alertbox").removeClass("alert-success");

                    $("#alertbox").addClass("alert-warning");
                    $("#alertbox").html(a.message)
                }
                else {
                    $("#alertbox").removeClass("alert-danger");
                    $("#alertbox").removeClass("alert-warning")
                    $("#alertbox").addClass("alert-success");
                    $("#alertbox").html(a.message)
                    if(attribute3!='')
                    {
                        setTimeout(function () {window.location.reload()}, 1500);
                    }
                }
            },
            contentType: "application/json",
            dataType: 'json'
        });
}