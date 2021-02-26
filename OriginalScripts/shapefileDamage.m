%% Get shapefiles to interact with damage functions
% Madeline Jones 4/19/2018

clear all
close all
clc


B = shaperead('newBldgs.shp'); %buildings point dataset 
% needs to have a field named BldgType

numBldgs = size(B,1);

for i = 1:numBldgs
    
    %var1 = string({B(i).BldgType}); %building type string
    var1 = "W1";
    %var2 = string({B(i).HML}); %num stories
    var3 = "HC"
    %var3 = string({B(i).BC}); %building code string
    lookup = var1 + var3; %building type + building code string
    
    PGA = double(B(i).PGA);
    
    [slight,moderate,extensive,complete] = GetDamage(lookup, PGA);
    
    B(i).Pslight = slight;
    B(i).Pmoderate = moderate;
    B(i).Pextensive = extensive;
    B(i).Pcomplete = complete;
end

shapewrite(B,'newBldgs_damage.shp');

 
 