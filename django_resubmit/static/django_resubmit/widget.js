;(function($, undefined){

   function ResubmitPreview(element, options) {
            this.element = element;
            this.options = $.extend(true, this.options, options || {});
            this._create();
    }

    $.extend(ResubmitPreview.prototype, {
        options: {
            maxDataLength: 1024 * 1024,
            trobberUrl: 'http://www.computerbase.de/design/throbber.gif',
            action: '/django_resubmit/'
        },

        _create: function(){
            var frame = $(this.element).closest('.file-upload');
            this.file_input = $(this.element);
            this.file_link = $('a', frame);
            this.key_input = $('input[type=hidden]', frame);
            this.preview = $('.resubmit-preview', frame);
            this.preview_image = $('.resubmit-preview__image', frame);
            this.changed();
        },

        changed: function(){
            //this.preview_image.attr('src', this.options.trobberUrl);
            
            this.localPreview();
            this.remotePreview();
        },

        updatePreview: function(src){
        console.log('up');
            this.preview_image.attr('src', src);
            if (src){
                this.preview_image.show().css('display', 'block');
            }
        },

        localPreview: function() {
            var self = this;
            var inputfile = this.file_input.get(0);
            var image = this.preview_image.get(0);

            // HTML5 FileAPI: Firefox 3.6+, Chrome 6+
            if(typeof(FileReader) != undefined && inputfile.files.item != undefined)
            {
                var reader = new FileReader();
                reader.onload = function(e){
                    var src = e.target.result;
                    self.updatePreview(src);
                }
                reader.readAsDataURL(inputfile.files.item(0));
            } else {
                // legacy browsers
                var base64ImgUriPattern = /^data:image\/(png|gif|ico|jpg|jpeg|bmp);base64/i;
                var file = inputfile.files && inputfile.files[0];
                if (file) {
                    // Check if we can access the serialized file via getAsDataURL(). firefox
                    if (file.getAsDataURL) {
                        var src = file.getAsDataURL();
                        if (src && src.length < this.options.maxDataLength && base64ImgUriPattern.test(src)) {
                            self.updatePreview(src);
                        }
                    }
                } else if (inputfile.value) {
                    /* maybe ie */
                    var src = this.value;
                    self.updatePreview(src);
                    
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
                },   
                success: function(jsonText) {
                    var data = JSON.parse(jsonText);
                    if (data.error) {
                        console.log(data.error)
                    } else {
                        self.key_input.val(data.key);

                        self.file_link.removeAttr('href');
                        if (data.upload && data.upload.name){
                            self.file_link.text(data.upload.name);
                        }

                        // In order to reduce the form submittion time,
                        // I want to prevert re-uploading a file on the actual form submit.
                        // Currently the file is saved on the server and it is sufficient to send only the `key`.
                        /* FIXME: unshure
                           If file will expired, user recieve a error message, and will have to select the file again.
                        */
                        self._clearFileInput();

                        if (data.preview) {
                            self.updatePreview(data.preview.url);
                        } else {
                        }
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
            if (obj) {
                obj.changed();
            } else {
                $(this).data('resubmit', new ResubmitPreview(this, options));
            }
        });

    };

    $(function(){
         $("input[type=file].resubmit").live('change', function(){
             $(this).resubmitPreview();
         }).resubmitPreview();
    });
})(django.jQuery);
