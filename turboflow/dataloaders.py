import torch
import numpy as np
import pytorch_lightning as pl

from torch.utils.data import Dataset, DataLoader

class FFMDataset(torch.utils.data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, input_img, mapping=None):
        'Initialization'
        
        # on single image
        assert input_img.shape[0] == input_img.shape[1]
        img_size = input_img.shape[0]
        
        eps = 1e-15

        coords = np.linspace(eps, 1, input_img.shape[0], endpoint=False)
        coords = np.stack(np.meshgrid(coords, coords), -1) # X x Y x 2
        self.inputs = torch.from_numpy(coords).float() #XY x 2 (x,y)
        
        if len(input_img.shape) == 2:
            input_img = input_img[:,:,None]
            
        self.target = torch.from_numpy(input_img).float()  #XxYx3 (RGB)
        
        assert self.inputs.shape[0] == self.target.shape[0]
        assert self.inputs.shape[1] == self.target.shape[1]

            
  def __len__(self):
        'Denotes the total number of samples'
        return 1

    
  def __getitem__(self, index):
        'Generates one sample of data'
        # Load data and get label
        X = self.inputs
        y = self.target

        return X, y
    

class FFMDataModule(pl.LightningDataModule):
    def __init__(self, img, training_downsampling_factor=2, batch_size = 1):
        
        super().__init__()
        self.batch_size = 1
        self.training_downsampling_factor = training_downsampling_factor
        self.img = img
        try:
            assert np.max(np.abs(img)) <= 1.0
        except:
            raise ValueError('Image is not within [-1, 1]. Max is %1.2f' % np.max(np.abs(img)))
        
    def prepare_data(self):
        self.train_dataset = FFMDataset(np.array(self.img[::self.training_downsampling_factor,::self.training_downsampling_factor]))
        self.valid_dataset = FFMDataset(np.array(self.img[::self.training_downsampling_factor,::self.training_downsampling_factor]))
        self.test_dataset = FFMDataset(np.array(self.img))
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size)

    def val_dataloader(self):
        return DataLoader(self.valid_dataset, batch_size=self.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size)


class MyDataset(torch.utils.data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, X, y):

        assert np.max(np.abs(y)) <= 1
        # assert np.max(np.abs(X)) <= 1

        'Initialization'
        print(X.shape)
        print(y.shape)
        try:
            assert X.shape[0] == y.shape[0]
            assert X.shape[1] == y.shape[1]
        except:
            print('Dimension error')
            print('X', X.shape)
            print('y', y.shape)

        # convert to torch and add an empty dimension for the batch
        self.inputs = torch.from_numpy(X).float() #XY x 2 (x,y)
        self.target = torch.from_numpy(y).float()  #XxYx3 (RGB)
        
        assert self.inputs.shape[0] == self.target.shape[0]
        assert self.inputs.shape[1] == self.target.shape[1]

            
  def __len__(self):
        'Denotes the total number of samples'
        return 1

    
  def __getitem__(self, index):
        'Generates one sample of data'
        # Load data and get label
        X = self.inputs
        y = self.target

        return X, y


class DataModule(pl.LightningDataModule):
    def __init__(self, train_data, val_data, test_data):
        
        super().__init__()
        self.batch_size = 1
        self.train_data = train_data
        self.test_data = test_data
        self.val_data = val_data
        
    def prepare_data(self):
        self.train_dataset = MyDataset(self.train_data[0], self.train_data[1])
        self.val_dataset = MyDataset(self.val_data[0], self.val_data[1])
        self.test_dataset = MyDataset(self.test_data[0], self.test_data[1])
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, 1)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, 1)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, 1)



class MyPatchDataset(torch.utils.data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, X, y):

        'Initialization'
        self.X = X
        self.y = y

        assert len(X) == len(y)

        self.size = len(X)


  def __len__(self):
        'Denotes the total number of samples'
        return self.size

    
  def __getitem__(self, index):
        'Generates one sample of data'
        # Load data and get label
        X = torch.from_numpy(self.X[index]).float() #XY x 2 (x,y)
        y = torch.from_numpy(self.y[index]).float()  #XxYx3 (RGB)

        return X, y


class PatchDataModule(pl.LightningDataModule):
    def __init__(self, train_data, val_data, test_data, batch_size=64):
        
        super().__init__()
        self.batch_size = 1
        self.train_data = train_data
        self.test_data = test_data
        self.val_data = val_data
        self.batch_size = batch_size
        
    def prepare_data(self):
        self.train_dataset = MyPatchDataset(self.train_data[0], self.train_data[1])
        self.val_dataset = MyPatchDataset(self.val_data[0], self.val_data[1])
        self.test_dataset = MyPatchDataset(self.test_data[0], self.test_data[1])
    
    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=8)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=True)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.batch_size, shuffle=True)

if __name__ == '__main__':
    pass