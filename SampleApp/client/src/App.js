import './App.css';
import React, { useRef, useState } from 'react';
import { ChakraProvider, Button, Spinner, Box, Text, Stack } from "@chakra-ui/react";
import { ArrowForwardIcon, DeleteIcon } from '@chakra-ui/icons';
import { ReactSketchCanvas } from "react-sketch-canvas";
import axios from 'axios';

const App = () => {
  const imageUrl = useRef(null);
  const [imageProcessing, setImageProcessing] = useState(false);
  const [imageId, setImageId] = useState('');
  const [recognizedResult, setRecognizedResult] = useState('');

  const classifyImage = async (backend) => {
    setImageId('');
    setImageProcessing(true);
    try {
      const imageData = await imageUrl.current.exportImage("png");
      const result = await axios.post(`${process.env.REACT_APP_API_SERVER}/tasks`, {
        img: imageData,
        backend: backend,
      });
      setImageId(result.data.task_id);
      await getResult(result.data.task_id);
    } catch(e) {
      console.error(e);
    }
  };

  const getResult = async (id) => {
    const result = await axios.get(`${process.env.REACT_APP_API_SERVER}/tasks/${id}`);
    if(result.data.task_status === 'SUCCESS') {
      setImageProcessing(false);
      setRecognizedResult(result.data.task_result);
    } else {
      console.log('waiting 5 sec...');
      setTimeout(getResult, 5000, id);
    }
  }

  const clearImage = async () => {
    setRecognizedResult('');
    await imageUrl.current.clearCanvas();
  }

  return (
    <ChakraProvider>
      <div className="app">
        <Box w='100%'
          p={2}
          borderBottom='1px'
          borderColor='gray.200'
          fontWeight='bold'
          marginBottom='0.5rem'
          paddingLeft='1rem'
          textAlign='left'
        >
          <Stack spacing={4} direction='row'>
            <img className="ryoko-icon" src="/ryoko_icon.png" alt="リョウコ"></img>
            <p>量子コンピューターで画像識別</p>
          </Stack>
        </Box>
        <div className="canvas">
          <Text className="text">
            {(recognizedResult === '') ? "枠内に 0 か 1 を描いて、量子コンピューターで識別してみましょう。" : `識別結果は ${recognizedResult.result} でした！使用したバックエンドは ${recognizedResult.backend} です。`}
          </Text>
          <ReactSketchCanvas
            ref={imageUrl}
            strokeWidth={30}
            strokeColor="black"
          />
          <Button
            className="classify-button"
            onClick={() => classifyImage('real')}
            leftIcon={<ArrowForwardIcon />}
            colorScheme='blue'
            variant='solid'
            size='lg'
          >
            実機で識別
          </Button>
          <Button
            className="classify-button"
            onClick={() => classifyImage('simulator')}
            leftIcon={<ArrowForwardIcon />}
            colorScheme='blue'
            variant='solid'
            size='lg'
          >
            シミュレーターで識別
          </Button>
          <Button
            className="classify-button"
            onClick={clearImage}
            leftIcon={<DeleteIcon />}
            colorScheme='blue'
            variant='solid'
            size='lg'
          >
            消去
          </Button>
          <div className="buttons-small">
            <Button
              className="classify-button-small"
              onClick={() => classifyImage('real')}
              colorScheme='blue'
              variant='solid'
              size='lg'
            >
              実機
            </Button>
            <Button
              className="classify-button-small"
              onClick={() => classifyImage('simulator')}
              colorScheme='blue'
              variant='solid'
              size='lg'
            >
              シミュレーター
            </Button>
            <Button
              className="classify-button-small"
              onClick={clearImage}
              leftIcon={<DeleteIcon />}
              iconSpacing="0"
              colorScheme='blue'
              variant='solid'
              size='lg'
            >
            </Button>
          </div>
        </div>

        { imageProcessing && (
          <div className="loading">
            <Spinner className='spinner' size='xl' />
            <Text className='job-message'>
              {(imageId.length === 0) && 'ジョブを開始中です...'}
              {(imageId.length > 0) && `ジョブ ID: ${imageId} を処理しています...`}
            </Text>
          </div>
        )}
      </div>
    </ChakraProvider>
  );
}

export default App;
