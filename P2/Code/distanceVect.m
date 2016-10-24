%Returns Distance Vector Based on Feature Library Calc
function vect = distanceVect(distAlg, featureChoice, lib, test_feat)

if distAlg == 1
    %PUT YOUR CODE HERE
    [m,n] = size(lib);
    dist = zeros(1,n);
    for i=1:n
       dist(i) = sum((test_feat{featureChoice}-lib{i}{featureChoice}).^2);
    end
    vect = dist;
    %disp(dist)
else
    [m,n] = size(lib);
    dist = zeros(1,n);
    for i=1:n
      top = dot(test_feat{featureChoice},lib{i}{featureChoice});
      bottom = sqrt(dot(test_feat{featureChoice},test_feat{featureChoice})) .* sqrt(dot(lib{i}{featureChoice},lib{i}{featureChoice}));
      dist(i) = acos((top ./ bottom));
    end
    vect = dist;
end

end