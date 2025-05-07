using System;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;

namespace GaussianSplatting.Runtime.Utils
{
    public static class NativeArrayHelper
    {
        public static unsafe Span<T> AsSpan<T>(this NativeArray<T> array) where T : unmanaged
        {
            return new Span<T>(NativeArrayUnsafeUtility.GetUnsafeBufferPointerWithoutChecks(array), array.Length);
        }
    }
}