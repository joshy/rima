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
    }

    load(image_paths, ct_image).then(function () {
        console.log("reading done")
    });

});