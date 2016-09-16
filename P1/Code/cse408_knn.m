% function to run KNN classification


function pred_label = cse408_knn(test_feat, train_label, train_feat, k, DstType)


if DstType == 1 %SSD
    %PUT YOUR CODE HERE
    [m,n] = size(train_feat);
    dist = zeros(1,n);
    for i=1:n
       dist(i) = sum((test_feat-train_feat(:,i)).^2);
    end
    %disp(dist)
elseif DstType == 2 %Angle Between Vectors
    %PUT YOUR CODE HERE
    [m,n] = size(train_feat);
    dist = zeros(1,n);
    for i=1:n
      top = dot(test_feat,train_feat(:,i));
      bottom = sqrt(dot(test_feat,test_feat)) .* sqrt(dot(train_feat(:,i),train_feat(:,i)));
      dist(i) = acos((top ./ bottom));
    end
    %disp(top);
    %disp(bottom);
    %disp(divided);
    %disp(dist);
elseif DstType == 3 %Number of words in common
    %PUT YOUR CODE HERE
    [m,n] = size(train_feat);
    dist = zeros(1,n);
    for i=1:n
       logical_train_col = logical(train_feat(:,i));
       logical_test = logical(test_feat);
       dist(i) = sum(and(logical_train_col,logical_test));
    end
    dist = -dist; % Why minus?
    %disp(dist);
end



%Find the top k nearest neighbors, and do the voting. 

[B,I] = sort(dist);

posCt=0;
negCt=0;
for ii = 1:k
    if train_label(I(ii)) == 1
        posCt = posCt + 1;
    elseif train_label(I(ii)) == 0
        negCt = negCt + 1;
    end    
end

if posCt >= negCt
    pred_label = 1;
else
    pred_label = 0;
end
