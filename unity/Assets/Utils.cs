using System.Threading.Tasks;
using UnityEngine.Networking;

public static class HttpDownloader
{
    public static async Task<byte[]> DownloadBytes(string url)
    {
        using var www = UnityWebRequest.Get(url);
        var op = www.SendWebRequest();

        while (!op.isDone)
            await Task.Yield();

        return www.downloadHandler.data;
    }
}

