import json,time,urllib.request,pathlib
out=pathlib.Path('/tmp/vamos-llm-comparison')
D='Eres Ana, una interlocutora para practicar español. Mantén el papel y el nivel A1-A2. Responde en español con una o dos frases cortas, máximo 40 palabras, y una sola pregunta pertinente. No expliques gramática. /no_think'
W='Eres profesor de español. Evalúa si la respuesta cumple la tarea. Corrige solo errores reales y conserva el significado. Si es correcta, dilo sin reescribir. No confundas variantes regionales ni preferencias de estilo con errores. Explica brevemente en español, máximo 80 palabras. /no_think'
cases=[
('cafe',D,[{'role':'user','content':'Eres camarera. Quiero un café con leche, pero no puedo tomar leche de vaca.'}]),
('memory',D,[{'role':'user','content':'Estamos en la estación. Quiero ir a Valencia mañana por la mañana, solo ida.'},{'role':'assistant','content':'Hay un tren a las nueve y otro a las once. ¿Cuál prefieres?'},{'role':'user','content':'El de las nueve. Confirma mi billete, por favor.'}]),
('past_tense',W,[{'role':'user','content':'Ejercicio A2: usa el pretérito indefinido para contar qué hiciste ayer. Respuesta: Ayer voy al mercado y compro dos manzanas.'}]),
('valid_subjunctive',W,[{'role':'user','content':'Tarea: expresa una condición y un deseo. Respuesta: Depende de que tengamos tiempo. Ojalá hubiera más trenes los domingos.'}]),
('agreement',W,[{'role':'user','content':'Tarea A1: di tu edad y qué te gusta. Respuesta: Soy veinte años y me gusta las películas españolas.'}]),
('regional',W,[{'role':'user','content':'Tarea: cuenta qué hiciste hoy. Respuesta: Hoy fui al mercado y compré unas frutillas para mis amigos.'}]),
('off_topic',W,[{'role':'user','content':'Tarea A1: escribe tu nombre, tu país y dónde vives. Respuesta: Los elefantes comen plantas y tienen orejas grandes.'}]),
('advanced',W,[{'role':'user','content':'Tarea B2: expresa una condición hipotética pasada y su consecuencia. Respuesta: Si habría sabido que el tren se retrasaba, habría salido más tarde de casa.'}]),
]
results=[]
for model in ['Qwen3.5-2B-Q4_K_M.gguf','SmolLM3-Q4_K_M.gguf']:
 for run in range(2):
  for name,system,msgs in cases:
   body={'model':model,'messages':[{'role':'system','content':system}]+msgs,'stream':True,'stream_options':{'include_usage':True},'max_tokens':200,'temperature':0.7,'top_p':0.8,'seed':42+run,'chat_template_kwargs':{'enable_thinking':False}}
   start=time.monotonic(); first=None; parts=[]; reasoning=[]; usage=None; finish=None
   try:
    req=urllib.request.Request('http://127.0.0.1:8349/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=120) as resp:
     for line in resp:
      if not line.startswith(b'data:'): continue
      data=line[5:].strip()
      if data==b'[DONE]': continue
      chunk=json.loads(data)
      if chunk.get('usage'): usage=chunk['usage']
      for choice in chunk.get('choices',[]):
       delta=choice.get('delta',{}); content=delta.get('content') or ''
       if content:
        if first is None: first=time.monotonic()-start
        parts.append(content)
       if delta.get('reasoning_content'): reasoning.append(delta['reasoning_content'])
       if choice.get('finish_reason'): finish=choice['finish_reason']
    rec={'model':model,'run':run+1,'case':name,'cold_switch':run==0 and name=='cafe','ttft':round(first,3) if first else None,'seconds':round(time.monotonic()-start,3),'text':''.join(parts),'reasoning':''.join(reasoning),'finish':finish,'usage':usage}
   except Exception as e: rec={'model':model,'run':run+1,'case':name,'error':str(e)}
   results.append(rec)
   (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
   print(json.dumps(rec,ensure_ascii=False),flush=True)
(out/'cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
