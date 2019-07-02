$(document).ready(function () {

    $(function() {

        var start = moment().subtract(29, 'days');
        var end = moment();

        function cb(start, end) {
            $('#report-range span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        }

        $('#report-range').daterangepicker({
            startDate: start,
            endDate: end,
            ranges: {
               'Today': [moment(), moment()],
               'Last 7 Days': [moment().subtract(6, 'days'), moment()],
               'Last 30 Days': [moment().subtract(29, 'days'), moment()],
               'This Month': [moment().startOf('month'), moment().endOf('month')],
               'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                'Last 6 Months': [moment().subtract(6, 'month').startOf('month'), moment()],
                'All time': ['12/03/2009', moment()]
            }
        }, cb);

        cb(start, end);

    });

    $('#report-range').on('apply.daterangepicker', function(ev, picker) {
      //do something, like clearing an input
        console.log(picker);
        var startDate = picker['startDate'];
        var endDate = picker['endDate'];
        console.log(startDate.format('DD-MM-YYYY') + ' - ' + endDate.format('DD-MM-YYYY'));
        document.getElementById('start_date').value = picker['startDate'].format('DD-MM-YYYY');
        document.getElementById('end_date').value = picker['endDate'].format('DD-MM-YYYY');
    /*
        const data = {
            start_date: picker['startDate'].format('DD-MM-YYYY'),
            end_date: picker['endDate'].format('DD-MM-YYYY'),
            csrfmiddlewaretoken: "{{ csrf_token }}"};

        $.get("{% url 'index' %}", data, function(data, status){
            console.log(`status is ${status} and data is: ${data}`)
        });
        */
      //alert(picker['endDate']['_d']);
      //alert(picker['startDate']['_d']);
    });
});