
(function($){

    function getSpinning() {
        return $('#preload-section').find('.spin').clone();
    }

    // load file list
    $(document).ready(function(){
        $('[data-toggle="file-list"]').on('click', function(event){
            event.preventDefault();
            var $table = $($(this).data('target'));
            var $tbody = $table.find('tbody');
            if ($tbody.length === 0) {
                console.warn('File list target container not found.');
                return;
            }
            $tbody.removeClass('text-danger');
            var href = $(this).attr('href');
            if (typeof href === 'undefined') {
                console.warn('No api url found.');
                return;
            }
            $(this).addClass('disabled');
            $table.removeClass('hidden');
            $tbody.html('');

            var $spin = $('<tr></tr><tr><td colspan="2"></td></tr>');
            $spin.find('td').append(getSpinning());
            $tbody.append($spin);

            $.ajax({
                url: href,
                method: 'GET',
                dataType: 'json',
                success: function(data, textStatus, jqXHR) {
                    $tbody.html('');
                    if (!data || !data.files) {
                        $tbody.addClass('text-danger');
                        $tbody.append($('<tr><td>Unexpected data returned.</td></tr>'));
                        return;
                    }
                    $.each(data.files, function(i, file) {
                        var $file = $('<tr></tr>');
                        var $path = $('<td class="file-path"></td>');
                        var $size = $('<td class="file-size"></td>');
                        $file.append($path);
                        $file.append($size);

                        $path.text(file.path);
                        $size.text(file.pretty_size);
                        $size.attr('data-filesize', file.size);

                        $tbody.append($file);
                    });
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $tbody.html('');
                    $tbody.addClass('text-danger');
                    $tbody.append($('<tr><td>Error retrieving file list.</td></tr>'));
                }
            });

        });
    });

})(jQuery);
