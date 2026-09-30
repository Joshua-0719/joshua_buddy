import ctypes
import struct

Carbon = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/Carbon.framework/Carbon')

# RegisterEventHotKey signature:
# OSStatus RegisterEventHotKey(UInt32 inHotKeyCode, UInt32 inHotKeyModifiers, EventHotKeyID inHotKeyID, EventTargetRef inTarget, OptionBits inOptions, EventHotKeyRef *outRef);

print("Carbon loaded:", Carbon)
