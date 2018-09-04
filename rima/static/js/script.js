$(function () {
    console.log('ready')

    var ct_image = $('#ct_image').get(0);
    var image_paths = $(ct_image).data('image-paths');

    cornerstoneWADOImageLoader.external.cornerstone = cornerstone;

    var config = {
        webWorkerPath : '../../static/js/cornerstoneWADOImageLoaderWebWorker.js',
        taskConfiguration: {
            'decodeTask' : {
                codecsPath: '../../static/js/cornerstoneWADOImageLoaderCodecs.js'
            }
        }
    };
    cornerstoneWADOImageLoader.webWorkerManager.initialize(config);

    function loadAndViewImage(imageId) {
        var element = document.getElementById('ct_image');
        console.log(element)
        try {
            var start = new Date().getTime();
            console.log(imageId)
            cornerstone.loadAndCacheImage(imageId).then(function (image) {
                console.log(image);
                var viewport = cornerstone.getDefaultViewportForImage(element, image);
                cornerstone.displayImage(element, image, viewport);
                if (loaded === false) {
                    cornerstoneTools.mouseInput.enable(element);
                    cornerstoneTools.mouseWheelInput.enable(element);
                    cornerstoneTools.wwwc.activate(element, 1); // ww/wc is the default tool for left mouse button
                    cornerstoneTools.pan.activate(element, 2); // pan is the default tool for middle mouse button
                    cornerstoneTools.zoom.activate(element, 4); // zoom is the default tool for right mouse button
                    cornerstoneTools.zoomWheel.activate(element); // zoom is the default tool for middle mouse wheel
                    loaded = true;
                }

            }, function (err) {
                console.error(err);
            });
        } catch (err) {
            alert(err);
        }
    }

    /*
    function load(imageIds, element) {
        cornerstone.enable(element);
        var stack = {
            currentImageIdIndex: 0,
            imageIds: imageIds
        };
        console.time('Loading');
        cornerstoneTools.mouseInput.enable(element);
        cornerstoneTools.keyboardInput.enable(element);
        cornerstoneTools.mouseWheelInput.enable(element);
        return cornerstone.loadImage(imageIds[stack.currentImageIdIndex])
            .then(function (image) {
                var viewport = cornerstone.getDefaultViewportForImage(element, image);
                cornerstone.displayImage(element, image, viewport);
                cornerstoneTools.addStackStateManager(element, ['stack']);
                cornerstoneTools.addToolState(element, 'stack', stack);
                cornerstoneTools.wwwc.activate(element, 1);
                cornerstoneTools.pan.activate(element, 4);
                cornerstoneTools.zoom.activate(element, 2);
                cornerstoneTools.stackScrollKeyboard.activate(element);
                cornerstoneTools.stackScrollWheel.activate(element);
                cornerstoneTools.stackPrefetch.enable(element, 3);
            });
    }*/

    //load(["wadouri:/images/ClearCanvas/USEcho/IM00001"], ct_image)
    //load(image_paths, ct_image)
    console.log(image_paths[0])
    loadAndViewImage(image_paths[0])
});