(function($){

    function makeImagePreview (inputFile, options) {
        var defaultOptions = {
            maxWidth: '150px',
            maxHeight: '150px'
        }
        
        var options = $.extend(true, defaultOptions, options);
        var base64ImgUriPattern = /^data:image\/((png)|(gif)|(jpg)|(jpeg)|(bmp));base64/i;
        var inputFileNode = $(inputFile).get(0);
        
        var image = $(inputFile).parent().find('img.resubmit')[0];
        if (image == undefined){
            image = $('<img class="resubmit"/>');
            image.insertAfter($(inputFile));
        }else{
           
            image = $(image);
        }
        
        image.css('max-width', options.maxWidth); 
        image.css('max-height', options.maxHeight);
        
        var file = inputFileNode.files && inputFileNode.files[0];
        var imageUrl= null;
        var hasUrl = false;
        // Check if we can access the serialized file via getAsDataURL().
        if (file) {
            /* firefox or chrome */
            if (file.getAsDataURL) {
                /* firefox */
                var src = file.getAsDataURL();
                if (src && base64ImgUriPattern.test(src)) {
                    imageUrl = src;
                }
            }
        } else if (inputFileNode.value) {
            /* maybe ie */
            imageUrl = this.value;
        } else {
            /* empty input */
            imageUrl = image.attr('src');
            hasUrl = !!imageUrl;
        }
        
        if (!imageUrl) {
            image.hide()
                 .removeAttr('src')
                 ;
        } else {
            image.attr({"src": imageUrl});
            image.show();
        }
    }

    $(function(){
         $("input[type=file].resubmit").live('change', function(){
            makeImagePreview($(this));

            $('img.resubmit').css('display', 'block'); //hack 
         });
    });
})(django.jQuery);
