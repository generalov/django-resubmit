;(function($, undefined){

   var t = $('script[src$="/django_resubmit/widget.js"]').attr('src'),
       STATIC_URL = t.substring(0, t.length - 'django_resubmit/widget.js'.length);

   function ResubmitPreview(element, options) {
            this.element = element;
            this.options = $.extend(true, this.options, options || {});
            this._create();
    }

    $.extend(ResubmitPreview.prototype, {
        options: {
            maxDataLength: 1024 * 1024,
            trobberUrl: STATIC_URL + 'django_resubmit/throbber.gif',
            action: '/django_resubmit/'
        },

        _create: function(){
            var frame = $(this.element).closest('.resubmit-widget');
            this.file_input = $(this.element);
            this.file_link = $('a', frame);
            this.key_input = $('input[type=hidden]', frame);
            this.preview = $('.resubmit-preview', frame);
            this.preview_image = $('.resubmit-preview__image', frame);
            this.initial = $('.resubmit-initial', frame);
        },

        changed: function(){
            this.localPreview();
            this.remotePreview();
        },

        updatePreview: function(src){
            if (src){
                this.preview_image.attr('src', src);
                this.preview.show();
            } else {
                this.preview.hide();
                this.preview_image.removeAttr('src');
            }
        },

        updatePreviewFromDataUrl: function(src) {
            var base64ImgUriPattern = /^data:image\/(png|gif|ico|jpg|jpeg|bmp);base64/i;
            if (src && src.length < this.options.maxDataLength && base64ImgUriPattern.test(src)) {
                this.updatePreview(src);
            } else {
                this.updatePreview('');
            }
        },

        localPreview: function() {
            var inputfile = this.file_input.get(0);
            var image = this.preview_image.get(0);

            // HTML5 FileAPI: Firefox 3.6+, Chrome 6+
            if(typeof(FileReader) != undefined) {
                if (inputfile.files[0]) {
	                var reader = new FileReader(),
	                    self = this;
	                reader.onload = function(e){
	                    var src = e.target.result;
                            self.updatePreviewFromDataUrl(src);
	                }
	                reader.readAsDataURL(inputfile.files[0]);
	           }
            } else {
                // legacy browsers
                var base64ImgUriPattern = /^data:image\/(png|gif|ico|jpg|jpeg|bmp);base64/i;
                var file = inputfile.files && inputfile.files[0];
                if (file) {
                    // Check if we can access the serialized file via getAsDataURL(). firefox
                    if (file.getAsDataURL) {
                        var src = file.getAsDataURL();
                        this.updatePreviewFromDataUrl(src);
                    }
                } else if (inputfile.value) {
                    /* maybe ie */
                    this.updatePreview(inputfile.value);
                    
                } else {
                    this.updatePreview(this.options.trobberUrl);
                }
            }
        },

        remotePreview: function(){
            var self = this,
                field = this.file_input.get(0),
                action = this.options.action + (this.key_input.val() ? this.key_input.val() + '/' : '');

            // Try not setting the response to application/json.
            // All "AJAX" file uploads must use iframes, thus a traditional 
            // form submit is required. The exception to this rule is use of
            // the XHR2 object, which most browsers don't implement.
            $(field.form).ajaxSubmit({
                url: action,
                dataType: 'text', 
                beforeSubmit: function(a,f,o) {
                    // keep just this field
                    var i;
                    for (i=a.length-1; i >= 0; --i) {
                       if (a[i].name != field.name) {
                           a.splice(i, 1); //remove
                       }    
                    }
                    self.file_link.removeAttr('href').html($('<img style="height: 16px; width: 16px"/>').attr('src', self.options.trobberUrl));
                },   
                success: function(jsonText) {
                    var data = JSON.parse(jsonText);
                    if (data.error) {
                        self.file_link.text(error);
                    } else {
                        self.key_input.val(data.key);

                        if (data.preview) {
                            self.updatePreview(data.preview.url);
                        } else {
                            self.updatePreview(false); // hide preiview
                        }

                        if (data.upload && data.upload.name){
                            self.file_link.text(data.upload.name);
                            self.initial.show()
                        }

                        // In order to reduce the form submittion time,
                        // I want to prevert re-uploading a file on the actual form submit.
                        // Currently the file is saved on the server and it is sufficient to send only the `key`.
                        /* FIXME: unshure
                           If file will expired, user recieve a error message, and will have to select the file again.
                        */
                        self._clearFileInput();

                    }
                }
           });                           
        },

        _clearFileInput: function(){
            // The only way to clear the file field is recreate it.
            // inspired by http://aspnetupload.com/Clear-HTML-File-Input.aspx
            function clearFileInput(oldInput) {
                var newInput = document.createElement("input");

                newInput.type = "file";
                newInput.name = oldInput.name;
                if (oldInput.id) newInput.id = oldInput.id;
                if (oldInput.className) newInput.className = oldInput.className;
                if (oldInput.style.cssText) newInput.style.cssText = oldInput.style.cssText;
                // copy any other relevant attributes

                oldInput.parentNode.replaceChild(newInput, oldInput);
                return newInput;
            }
            this.file_input = $(clearFileInput(this.file_input.get(0)));
        }
    });

    $.fn.resubmitPreview = function(options){

        return this.each(function(){
            var obj = $(this).data('resubmit');
            if (!obj) {
                obj = new ResubmitPreview(this, options);
                $(this).data('resubmit');
            }
            obj.changed();
        });

    };

    $(function(){
         $("input[type=file].resubmit-input").live('change', function(){
             $(this).resubmitPreview();
         });
    });
})(django.jQuery);
