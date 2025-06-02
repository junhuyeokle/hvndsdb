using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;

public static class HttpDownloader
{
    public static async Task<byte[]> DownloadBytes(string url)
    {
        using UnityWebRequest www = UnityWebRequest.Get(url);
        var op = www.SendWebRequest();

        while (!op.isDone)
            await Task.Yield();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError($"[HttpDownloader] Failed to download: {url}\n{www.error}");
            return null;
        }

        return www.downloadHandler.data;
    }

    public static async Task<string> DownloadText(string url)
    {
        using UnityWebRequest www = UnityWebRequest.Get(url);
        var op = www.SendWebRequest();

        while (!op.isDone)
            await Task.Yield();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError($"[HttpDownloader] Failed to download text: {url}\n{www.error}");
            return null;
        }

        return www.downloadHandler.text;
    }
}

