%Returns a feature vector of extracted features from image

function featVect = featureExtraction(imageFileName)
    % Read in an image and convert it to RGB
    [I,C] = imread(imageFileName);
    if ~isempty(C)
        rgbImage = ind2rgb(I,C);
    end
    image(rgbImage);
    % Average Pixel Color
    % Since PNG is put in MATLAB with all black background
    % we are going to not have anything in average if it is
    % pure black (0,0,0) so the average for the image is not
    % skewed
    re = rgbImage(:,:,1);
    gr = rgbImage(:,:,2);
    bl = rgbImage(:,:,3);
    count = 0;
    reTotal = 0;
    grTotal = 0;
    blTotal = 0;
    for i = 1:numel(re)
        if re(i) == 0 && gr(i) == 0 && bl(i) == 0
            %DO NOTHING FOR ALL BLACK
        else
            count = count + 1;
            reTotal = reTotal + re(i);
            grTotal = grTotal + gr(i);
            blTotal = blTotal + bl(i);
        end
    end
    rgbPixelAverage = [reTotal,grTotal,blTotal] ./ count;
    
    featVect = {rgbPixelAverage};
end