from channels.layers import get_channel_layer
layer = get_channel_layer()
print(layer.prefix, layer.hosts)
