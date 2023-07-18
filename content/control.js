$(document).ready(function() {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        var my_object = channel.objects.MyObject;
        $("#btn0").click(function() {
            my_object.createAccount($().val());
        });
        $("#btn1").click(function() {
            my_object.getAllAccount($().val());
        });
        $("#btn2").click(function() {
            my_object.currentAccount($().val());
        });
        $("#btn3").click(function() {
            my_object.startMinning($("#txt0").val());
        });
        $("#btn4").click(function() {
            my_object.addToBlockchain($("#txt1").val());
        });
        $("#btn5").click(function() {
            my_object.run($("#txt2").val());
        });
        $("#btn6").click(function() {
            my_object.listAllNodes($().val());
        });
        $("#btn7").click(function() {
            my_object.listBlockchain($().val());
        });
        $("#btn8").click(function() {
            my_object.sendTransaction($("#txt3").val(),$("#txt4").val(),$("#txt5").val(),$("#txt6").val());
        });
        $("#btn9").click(function() {
            my_object.showTranList($().val());
        });

        // var my_timer = channel.objects.MyTimer;
        // my_timer.timeout.connect(function() {
        //     $("#ctr0").text(1 + parseInt($("#ctr0").text()));
        // });
        //
        // my_timer.start(2000);
    })
})
