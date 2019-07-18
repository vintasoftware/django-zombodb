(function($) {
    $(document).ready(function () {
        var scoreAllZero = (
            $('td.field-_zombodb_score')
            .toArray()
            .every(function (x) { return x.textContent == '0.0' }));
        if (scoreAllZero) {
            $('th.column-_zombodb_score').remove();
            $('td.field-_zombodb_score').remove();
        }
    });
})(django.jQuery || jQuery);
