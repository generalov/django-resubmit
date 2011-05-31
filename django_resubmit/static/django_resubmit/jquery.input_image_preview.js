/**
 * Show image preview for <input type="file"> form field.
 *
 * $(":file").inputImagePreview({
 *      place: function(frame) { $(this).before(frame); },
 *      // <a href="/image.jpg">image.jpg</a>
 *      // <input type="file">
 *      // display any url when input is empty
 *      imageUrl: function(){ return $(this).prevAll("a:first").attr("href");}
 * });
 * 
 * @author Evgeny V. Generalov <e.generalov@gmail.com>
 */

(function($){
    var pluginName = "inputImagePreview";
    var defaultOptions = {
        maxWidth: 100,
        imageUrl: null,
        containerClass: 'image-preview',
        imageClass: 'image-preview-picture',
        atServerClass: 'atserver',
        widthClass: 'width',
        heightClass: 'height',
        dom: null,
        image: null,
        url: 'javascript:void(0)'
    };
    var base64ImgUriPattern = /^data:image\/((png)|(gif)|(jpg)|(jpeg)|(bmp));base64/i;


    $.extend($.fn, {
        inputImagePreview: function(options) {
            return this.each(function(){
                var $this = $(this);
                if ($this.data(pluginName)) {
                    var inputImagePreview = $this.data(pluginName);
                    $.extend(true, inputImagePreview, options);
                    inputImagePreview.render();
                } else {
                    $this.data(pluginName, new InputImagePreview(this, options));
                }
            })
        }
    });

    var InputImagePreview = function(elem, options) {
        var self = this;
        
        this.inputFile = $(elem);
        this.options = $.extend(true, defaultOptions, options);

        if (!this.options.dom) {
            this.dom = $('<a/>', {'href':options.url, 'target': '_blank',
                                        'class':this.options.domClass}).append(
                this.image =   $('<img/>', {'class':this.options.imageClass})).append(
                this.width = $('<span></span>', {'class':this.options.widthClass}).append('×').append(
                this.height = $('<span></span>', {'class':this.options.heightClass})));
            this.dom.insertAfter(this.inputFile);
        } else {
            this.dom = this.options.dom;
            this.image = this.options.image || this.dom.find('img');
            this.width = this.options.width || this.dom.parent().find('.'+this.options.widthClass);
            this.height = this.options.height || this.dom.parent().find('.'+this.options.heightClass);
            this.options.url = this.dom.attr('href');
        }

        this.inputFile.bind({
            change: function(){self.render()}
        });
        
        this.dom.addClass(this.options.domClass);
        this.image.addClass(this.options.imageClass);

        this.render();
    }

    $.extend(InputImagePreview.prototype, {
        updateImage: function() {
            var inputFileNode = this.inputFile.get(0);
            var image = this.image;
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
                imageUrl = this.options.thumbnailUrl || image.attr('src');
                hasUrl = !!imageUrl;
            }
            
            if (!imageUrl) {
                image.hide()
                     .removeAttr('src')
                     ;
            } else {
                image.attr({"src": imageUrl})
                     .css({'max-width': this.options.maxWidth,
                           'max-height': this.options.maxHeight})
                     ;
                if (hasUrl) {
                    image.addClass(this.options.atServerClass);
                } else {
                    image.removeClass(this.options.atServerClass);
                    // adjust width and height
                    var img = new Image();
                    img.src=imageUrl;
                    // we must wait for image loading, therefore we
                    // take img.width and img.height values assyncroniusly
                    setTimeout(function(c, img) {
                        c.width.text(img.width);
                        c.height.text(img.height)}, 1, this, img);
                }
                image.show();
            }
        },
        updateContainer: function() {
            if (this.image.hasClass(this.options.atServerClass)) {
                this.dom.attr({'href': this.options.url});
            } else {
                this.dom.removeAttr('href');
            }
        },
        render: function() {
            this.updateImage();
            this.updateContainer();
        }
    });

})(jQuery || django.jQuery);
