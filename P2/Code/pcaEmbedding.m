neuralNet = load('../DeepNetFeature/feature_vgg_f.mat');
[m,n] = size(neuralNet.image_feat);
feature_matrix = [];
names = {};
for i=1:n
    names = [names,neuralNet.image_feat(i).name];
    feature_matrix = [feature_matrix,neuralNet.image_feat(i).feat];
end

[coeff,score,somethingelse] = pca(feature_matrix);
axis image
scatter(coeff(:,1)*1000,coeff(:,2)*1000);
hold on
for i=1:n
    [I,C] = imread(fullfile('../Data/Database',names{i}));
    if ~isempty(C)
        rgbImage = ind2rgb(I,C);
    end
    imageForGraph = imagesc([coeff(i,1)*1000 coeff(i,1)*1000-5],[coeff(i,2)*1000 coeff(i,2)*1000-25],rgbImage);
    imageForGraph.AlphaData = .5;
end