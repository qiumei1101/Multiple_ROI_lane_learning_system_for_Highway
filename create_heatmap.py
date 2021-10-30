heatmap = np.zeros_like(im[:,:,0]).astype(np.float)
h,w = im.shape[:2]
y_list={}
y_list=y_list.fromkeys(range(h))
for id in range(h):
    y_list[id]=[]
for veh in vehicles:

    if veh[-1]>=0.0:
        heatmap[veh[1]][veh[0]] += 1

heatmap[heatmap <= 1] = 0
heatmapimg = np.array(heatmap * 255, dtype = np.uint8)
heatmap = cv2.applyColorMap(heatmapimg, cv2.COLORMAP_JET)
heatmap = heatmap/255
import matplotlib.cm as cmap

plt.imshow(heatmap,cmap=cmap.hot)
plt.savefig("heatmap.png")
# # backtorgb = cv2.cvtColor(heatmap,cv2.COLOR_GRAY2RGB)
plt.colorbar()
plt.show()