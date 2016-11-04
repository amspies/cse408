neuralNet = load('../DeepNetFeature/feature_vgg_f.mat');
[m,n] = size(neuralNet.image_feat);
feature_matrix = [];
names = {};
for i=1:n
    names = [names,neuralNet.image_feat(i).name];
    feature_matrix = [feature_matrix; reshape(neuralNet.image_feat(i).feat,[1 4096])];
end

[coeff,score,somethingelse] = pca(feature_matrix);
axis image
scatter(score(:,1),score(:,2));
hold on
for i=1:n
    [I,C] = imread(fullfile('../Data/Database',names{i}));
    if ~isempty(C)
        rgbImage = ind2rgb(I,C);
    end
    imageForGraph = imagesc([score(i,1) score(i,1)- 4],[score(i,2) score(i,2) - 7],rgbImage);
    imageForGraph.AlphaData = .5;
end