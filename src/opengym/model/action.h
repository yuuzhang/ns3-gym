/* -*-  Mode: C++; c-file-style: "gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2018 Piotr Gawlowicz
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Piotr Gawlowicz <gawlowicz.p@gmail.com>
 *
 */

#ifndef OPENGYM_ACTION_H
#define OPENGYM_ACTION_H

#include "ns3/object.h"
#include "ns3/simulator.h"
#include <map>

namespace ns3 {

class OpenGymDataContainer;

class OpenGymAction : public Object
{
public:
  OpenGymAction ();
  virtual ~OpenGymAction ();

  static TypeId GetTypeId ();
  std::string m_actionString;

  bool AddActionContainer(Ptr<OpenGymDataContainer> container);
  Ptr<OpenGymDataContainer> GetActionContainer(uint32_t idx);
  std::vector<Ptr<OpenGymDataContainer> > GetActionContainers();

protected:
  // Inherited
  virtual void DoInitialize (void);
  virtual void DoDispose (void);

private:
  std::vector<Ptr<OpenGymDataContainer> > m_containers;
};

} // end of namespace ns3

#endif /* OPENGYM_ACTION_H */

