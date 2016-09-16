posFolder = '../Data/pos';
negFolder = '../Data/neg';

voc = {}; %vocabulary is cell array of character vectors.
voc = buildVoc(posFolder,voc);
voc = buildVoc(negFolder,voc);
voc


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

files = dir(fullfile(posFolder,'*.txt'));

feat = [];
label = [];
for file = files'
    label = [label,1];
    feat_vec = cse408_bow(fullfile(posFolder,file.name), voc);
    feat = [feat,feat_vec'];
end

files = dir(fullfile(negFolder,'*.txt'));

for file = files'
    label = [label,0];
    feat_vec = cse408_bow(fullfile(negFolder,file.name), voc);
    feat = [feat,feat_vec'];
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


lines = zeros(3,30);

for distNum=1:3
  for j=1:30
    correct_ct = 0;
    DistType = distNum; % test different distance type
    K = j; % test different K.

    for ii = 1:size(label,2)
        train_label = label;
        train_label(ii) = [];
        train_feat = feat;
        train_feat(:,ii) = [];
        pred_label = cse408_knn(feat(:,ii),train_label,train_feat,K, DistType);
        if pred_label == label(ii)
            correct_ct = correct_ct + 1;
        end
        disp(strcat('Document', int2str(ii), ' groundtruth ', int2str(label(ii)), ' predicted as ', int2str(pred_label)));
    end
    accuracy = correct_ct / size(label,2);
    disp(accuracy);
    lines(distNum,j) = accuracy;
  end
end

plot([1:30],lines(1,:),[1:30],lines(2,:),[1:30],lines(3,:));
legend('SSD', 'Angle Between Vectors', 'Number of Words in Common')
title('Accuracy of KNN Based on K Value and Distance Function')
ylabel('Accuracy')
xlabel('Value of K')
print -djpg output_plot.jpg