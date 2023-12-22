from typing import List


def generate_input_from_url(url: str, pad: str) -> List[str]:
  parts = []
  try:
    ssub = url.find('[')
    msub = url.find('-',ssub)
    esub = url.find(']',msub)
    beg = url[0:ssub]
    end = url[esub+1:]
    fst = url[ssub+1:msub]
    snd = url[msub+1:esub]
    for i in range(int(fst), int(snd)+1):
      if pad:
        pic = str(i).rjust(len(snd), pad)
      else:
        pic = str(i)
      parts.append(beg+pic)
  except ValueError:
    pass
    
  files = []
  for f in parts:
    for rest in generate_input_from_url(end, pad):
      files.append(f + rest)
      
  return files or [url]