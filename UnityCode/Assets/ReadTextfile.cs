using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System;
using System.Threading;
using System.Text;

public class ReadTextfile : MonoBehaviour
{
    
    public GameObject bone;
    
    public string IP = "127.0.0.1"; //
    public int Port = 1234;
    public byte[] dane;
    public Socket client;
    // Use this for initialization
    public void Changing()
    {
        client = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        client.Connect(IP, Port);//connecting port 
        dane = System.Text.Encoding.ASCII.GetBytes(transform.localScale.ToString());//decode string  data into byte for sending 
        client.Send(dane);//send data to port 
        byte[] b = new byte[1024];
        int k = client.Receive(b);//recive data from port coming from python script 
        string szReceived = System.Text.Encoding.ASCII.GetString(b, 0, k);//coming data is in bytes converting into string 
        if (client.Connected)
        {
            Debug.Log("Getting data from Python");
            createBones(szReceived);
        }
        else
        {
            Debug.Log(" Not Connected");

        }
        client.Close();


    }
    void Start()
    {
        //calling that function of sending and reciveing data 
        Changing();
    }

    void Update()
    {
        //calling that function of sending and reciveing data 
        Changing();

    }

    private void createBones(string inp_ln)
    {
        GameObject[] killEmAll;
        killEmAll = GameObject.FindGameObjectsWithTag("bone");
        for (int i = 0; i < killEmAll.Length; i++)
        {
            Destroy(killEmAll[i].gameObject);
        }
        Debug.Log(inp_ln);

        inp_ln = inp_ln.Substring(1, inp_ln.Length - 1);
        string[] bonePositions = inp_ln.Split(')');

        for (int i = 0; i < bonePositions.Length; i++)
        {
            bonePositions[i] = bonePositions[i].Substring(0, bonePositions[i].Length);
            bonePositions[i] += ")";
            if (i > 0)
            {
                bonePositions[i] = bonePositions[i].Substring(2);
            }
        }

        for (int i = 0; i < bonePositions.Length - 1; i++)
        {
            int startIndex = bonePositions[i].IndexOf('(');
            int endIndex = bonePositions[i].IndexOf(')');
            string[] xy = bonePositions[i].Substring(startIndex + 1, endIndex - 1 - startIndex).Split(',');

            Vector2 pos = new Vector2(float.Parse(xy[0]) / 32, float.Parse(xy[1]) / 72); //setup position in world of the bones.
            Instantiate(bone, pos, transform.rotation);
        }
    }
}