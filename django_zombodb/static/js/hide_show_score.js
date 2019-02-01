(function($) {
    $(document).ready(function () {
        var scoreAllZero = (
            $('td.field-_zombodb_score')
            .text()
            .split('')
            .every(function (x) { return x == '0' }));
        if (scoreAllZero) {
            $('th.column-_zombodb_score').remove();
            $('td.field-_zombodb_score').remove();
        }
    });
})(django.jQuery);
