
#%%
#basic
from utilref import *
from torch.utils.data import Dataset

labeldatasetsize = 30000


class ToTensor:

    def __init__(self) -> None:
        pass

    def __call__(self, x):
        return x


class labeldataset(Dataset):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def __readFileInterface_Folder(folder, pathlist):
        mlist = [os.path.join(folder, m) for m in pathlist]
        mlist = [cv.imread(m, 1) for m in mlist]
        mlist = [m.astype(np.float32) / 255 for m in mlist]
        return mlist

    @staticmethod
    def __readFileInterface_Zip(zipf, pathlist):
        from zipfile import ZipFile
        zipf = ZipFile(zipf)
        mlist = [zipf.read(imgf) for imgf in pathlist]
        mlist = [np.frombuffer(m, dtype=np.uint8) for m in mlist]
        mlist = [cv.imdecode(m, 1) for m in mlist]
        mlist = [m.astype(np.float32) / 255 for m in mlist]
        return mlist

    def init(self, path, selection, pathtype='fld'):
        selection = Xls2ListList(selection)
        selection = [s[0] for s in selection]
        selection = [s for s in selection if s is not None]

        if pathtype == 'fld':
            reader = labeldataset.__readFileInterface_Folder
        elif pathtype == 'zip':
            reader = labeldataset.__readFileInterface_Zip
        else:
            raise TypeError(f'inproper path type {pathtype}')

        self.cacheSrc = reader(path, [f'spl/{p}' for p in selection])
        cacheLbl = reader(path, [f'lbl/{p}' for p in selection])
        self.cacheLbl = [
            cv.threshold(p, 0.5, 1, cv.THRESH_BINARY)[1][:, :, 0]
            for p in cacheLbl
        ]
        return self

    def __len__(self):
        return labeldatasetsize

    @staticmethod
    def dataEnhance(src, lbl, rotenh=True, zomenh=True, flpenh=True):
        dttp = [src, lbl]

        #rot
        def rot(m, the):
            #theta in [-pi/2,pi/2]
            #assert right squared img0 here
            rotmat = np.array([
                [np.cos(the), -np.sin(the)],
                [np.sin(the), np.cos(the)],
            ])

            l0 = m.shape[0]
            Y, X = np.arange(l0, dtype=np.float32), np.arange(l0,
                                                              dtype=np.float32)
            X, Y = np.meshgrid(X, Y)
            Y -= l0 * 0.5
            X -= l0 * 0.5
            Xp = rotmat[0, 0] * X + rotmat[0, 1] * Y
            Yp = rotmat[1, 0] * X + rotmat[1, 1] * Y
            X = Xp
            Y = Yp
            Y += l0 * 0.5
            X += l0 * 0.5
            m = cv.remap(m, Xp, Yp, cv.INTER_LINEAR)
            return m

        if rotenh:
            the_u = np.pi / 12
            the_l = -the_u
            the = np.random.rand() * (the_u - the_l) + the_l
            dttp = [rot(m, the) for m in dttp]

        #zoom
        def zoom(m, rate):
            l0 = m.shape[0]
            X = np.arange(l0).reshape([1, l0]).astype(np.float32)
            Y = np.arange(l0).reshape([l0, 1]).astype(np.float32)
            XY = np.array(np.meshgrid(X, Y))
            XY -= l0 / 2
            XY /= rate
            XY += l0 / 2
            return cv.remap(m, *XY, cv.INTER_LINEAR)

        if zomenh:
            rate = (np.random.rand() * 0.2) + 0.9
            dttp = [zoom(m, rate) for m in dttp]

        #flip
        def flip(m, reallyflip: bool):
            if reallyflip:
                return np.flip(m, axis=1)  # flip lr
            else:
                return m

        if flpenh:
            reallyflip = (np.random.rand() < 0.5)
            dttp = [flip(m, reallyflip) for m in dttp]
            dttp = [np.ascontiguousarray(m) for m in dttp]

        #thresh for those cv.INTER_LINEAR transformation
        #dttp[1] = cv.threshold(dttp[1], 0.5, 1, cv.THRESH_BINARY)[1]

        #give back channel dim
        dttp = [
            m if len(m.shape) == 3 else m.reshape(m.shape + (1, ))
            for m in dttp
        ]
        src, lbl = dttp
        return src, lbl

    #idx in [0,1)

    def readSample(self, idx):
        idx = int(len(self.cacheSrc) * idx)

        src = self.cacheSrc[idx]
        lbl = self.cacheLbl[idx]

        # shape standardlize included
        src, lbl = labeldataset.dataEnhance(src, lbl)

        return ToTensor()(src), ToTensor()(lbl)

    def __getitem__(self, idx):
        return self.readSample(np.random.random())

#%%
#go

background = r'C:\file\code\wtutility\output\opdar_plane\spl_none'
planesrc = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all'
planesrc=labeldataset().init(planesrc,r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selall.xlsx")
background=AllFileIn(background)

samplenum=3*3
npp=nestedPyPlot([3,3],[2,1],plt.figure())
for oi in range(samplenum):
    
    spl,lbl=planesrc[0]
    spl=cv.cvtColor(spl,cv.COLOR_BGR2RGB)
    
    def singleAxisAABB(ax,pic):
        if len(pic.shape)==3:
            pic=pic[:,:,0]
        sum=np.sum(pic,axis=ax)
        coorstart=0
        for i in range(len(sum)):
            if sum[i]>0:
                coorstart=i
                break
        
        coorend=0
        for i in range(len(sum)-1,0-1,-1):
            if sum[i]>0:
                coorend=i
                break
        
        return [coorstart,coorend]
    aabb=np.moveaxis(np.array([singleAxisAABB(ax,lbl) for ax in [0,1]]),0,1)

    
    
    bg=cv.imread(background[int(np.random.random()*len(background))]).astype(np.float32)/255
    bg=cv.cvtColor(bg,cv.COLOR_BGR2RGB)
    
    
    #simply copy
    #result=np.copy(bg)
    #np.copyto(result,spl,where= lbl>0.5)
    result=cv.seamlessClone(spl,bg,lbl[:,:,0],[0,0],cv.MIXED_CLONE)
    
    npp.subplot(oi,0)
    plt.imshow(result)
    npp.subplot(oi,1)
    plt.imshow(lbl)
